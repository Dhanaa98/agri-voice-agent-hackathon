"""Plant disease diagnostic conversation agent ("Hey Plant").

Voice-only, multi-turn diagnosis: the farmer describes a symptom, the
agent asks 1-2 targeted follow-up questions to narrow the cause, then
gives a diagnosis that explicitly weighs current weather (from the shared
the active farm) -- e.g. boosting fungal/water-mould likelihood under high
humidity and recent rainfall, per the brief's cross-domain reasoning
requirement.

Reliability design (per the brief): the narrowing itself is deterministic
-- keyword matching against plant_data.py's symptom categories and
weather-based score adjustments -- not left to the LLM to infer. The LLM
is used only for two things: (1) turning a matched follow-up question
into natural phrasing, and (2) phrasing the final diagnosis summary. It
never decides which cause is more likely.

Also does a deterministic biotic-vs-abiotic sanity check (see
has_abiotic_hint / _ABIOTIC_HINT_MARKERS): if the farmer's own wording
suggests a nonliving cause (unrelated plants nearby affected, no spread
over time, a sharp margin, a named chemical/sprinkler/fertilizer issue),
the final diagnosis surfaces a caveat instead of confidently blaming a
pathogen. Heuristic sourced from Timmerman et al., Univ. of
Nebraska-Lincoln Extension EC1270 (2014).

Two separate weather mechanisms, at two different levels of precision:
(1) weather_adjusted_causes() ranks the broad CAUSE CATEGORIES (fungus vs.
nutrient vs. insect etc.) using a coarse humid/dry check -- always runs,
every symptom category has likely_causes. (2) weather_matches_trigger()
checks a SPECIFIC NAMED DISEASE's own sourced weather condition (e.g. rice
blast's "RH 93-99%, night temp 15-20C") -- only runs, and only gets
mentioned in the diagnosis, when that disease's plant_data.py entry
actually has a WeatherTrigger. A disease with no sourced trigger gets no
weather commentary at all, rather than a guessed one -- weather only
enters the conversation where we actually have the data for it.

Region-aware control recommendations (see get_control_for_region()): each
NamedDisease's `control` is a list of RegionalControl entries rather than
one string -- universal agronomic practice (crop rotation, sanitation,
timing) always shows regardless of the farmer's location, while a
region-specific entry (a named fungicide product, a variety bred/released
for one place) only shows when the active farm's country_code actually matches
that entry's country_codes. Unknown or non-matching regions get ONLY the
universal entries, never a guess at which country's advice might apply --
the agent is deliberately worldwide-neutral rather than defaulting to
whichever country most of the current source material happens to come
from. country_code is set on the active farm by the Weather domain from its
geocoding lookup (see weather.py), so this only activates once "Hey
Weather" has run at least once in the conversation.

This is a PlantSession: one instance per diagnostic conversation, holding
just enough state to ask up to two follow-up questions before summarizing.
main.py is responsible for creating one when a "Hey Plant" wakeword fires
and feeding it each ASR transcript in turn until it reports done.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import llm_client
from ..farm_state import FarmProfile
from .plant_data import (
    SYMPTOM_CATEGORIES,
    FollowUpQuestion,
    NamedDisease,
    RegionalControl,
    SymptomCategory,
    WeatherTrigger,
    get_named_diseases,
)

MAX_FOLLOW_UPS = 2

# Keyword -> symptom category, used to map free-text symptom descriptions
# onto the structured categories in plant_data.py without an LLM call.
# Multi-word/more-specific phrases are listed before shorter substrings they
# contain (e.g. "ring spot" before "spot") since match_symptom_category
# returns the first hit in iteration order.
#
# Vocabulary expanded from Timmerman et al., "Common Signs and Symptoms of
# Unhealthy Plants" (Univ. of Nebraska-Lincoln Extension EC1270, 2014) -- a
# general symptom-terminology glossary (not crop- or disease-specific) used
# here only to widen which farmer phrasings map onto our existing
# SYMPTOM_CATEGORIES, not as a source of any new category or disease.
_SYMPTOM_KEYWORDS: dict[str, str] = {
    "wilt": "wilt",
    "droop": "wilt",
    "limp": "wilt",
    "ring spot": "mosaic",
    "ringspot": "mosaic",
    "shot hole": "leaf_spot",
    "shot-hole": "leaf_spot",
    "witches broom": "little_leaf",
    "witches' broom": "little_leaf",
    "stubby root": "galls",
    "spot": "leaf_spot",
    "spots": "leaf_spot",
    "lesion": "leaf_spot",
    "blotch": "leaf_spot",
    "fleck": "leaf_spot",
    "pustule": "leaf_spot",
    "mildew": "leaf_spot",
    "yellow": "yellowing",
    "yellowing": "yellowing",
    "pale": "yellowing",
    "chlorosis": "yellowing",
    "chlorotic": "yellowing",
    "bronzing": "yellowing",
    "bronze": "yellowing",
    "mosaic": "mosaic",
    "mottle": "mosaic",
    "mottled": "mosaic",
    "patchy": "mosaic",
    "curl": "distortion",
    "curled": "distortion",
    "twist": "distortion",
    "pucker": "distortion",
    "distort": "distortion",
    "misshapen": "distortion",
    "bleach": "distortion",
    "small leaves": "little_leaf",
    "tiny leaves": "little_leaf",
    "bunched": "little_leaf",
    "broom": "little_leaf",
    "stunt": "little_leaf",
    "stunted": "little_leaf",
    "gall": "galls",
    "swelling": "galls",
    "lump": "galls",
    "bump": "galls",
    "canker": "drying_blight",
    "dieback": "drying_blight",
    "die back": "drying_blight",
    "scorch": "drying_blight",
    "rot": "drying_blight",
    "rotting": "drying_blight",
    "dry": "drying_blight",
    "dried": "drying_blight",
    "brown": "drying_blight",
    "blight": "drying_blight",
    "dying": "drying_blight",
}

# Phrasings that suggest the problem may not be biological at all -- an
# uneven/nonliving cause (watering, nutrients, chemical drift, mechanical
# damage) rather than a pathogen. Heuristic from EC1270: biotic problems
# have an uneven margin, are randomly distributed, and spread to nearby
# related plants over time; abiotic problems have a sharp margin, a uniform
# distribution pattern, affect unrelated species alike, and don't spread.
_ABIOTIC_HINT_MARKERS = (
    "only this one plant",
    "just this one plant",
    "other kinds of plants",
    "different kinds of plants",
    "different plants too",
    "not spreading",
    "hasn't spread",
    "has not spread",
    "sharp line",
    "sharp edge",
    "clear line",
    "sprinkler",
    "fertilizer",
    "chemical",
    "herbicide",
    "spray drift",
)

# Weather condition keyword -> causes it boosts, used to weight the final
# diagnosis deterministically instead of trusting the LLM's judgment.
_HUMID_BOOSTED_CAUSES = {"fungus", "water_mould", "bacteria"}
_DRY_BOOSTED_CAUSES = {"nutrient", "mite", "insect"}


def match_symptom_category(text: str) -> str | None:
    """Find the first symptom category whose keywords appear in the text."""
    lowered = text.lower()
    for keyword, category in _SYMPTOM_KEYWORDS.items():
        if keyword in lowered:
            return category
    return None


def has_abiotic_hint(text: str) -> bool:
    """True if the farmer's own wording suggests a nonliving cause (water,
    nutrients, chemical, mechanical) rather than a pathogen -- e.g. multiple
    unrelated plants affected, no spread over time, a sharp margin, or a
    named chemical/sprinkler/fertilizer issue. Deterministic keyword check,
    not an LLM judgment call -- see _ABIOTIC_HINT_MARKERS."""
    lowered = text.lower()
    return any(marker in lowered for marker in _ABIOTIC_HINT_MARKERS)


def weather_adjusted_causes(category: SymptomCategory, farm: FarmProfile) -> list[tuple[str, str]]:
    """Return (cause, explanation) pairs, weather-boosted causes first.

    This is the deterministic cross-domain hook: current humidity and
    recent rainfall on the active farm shift which cause is presented first,
    without an LLM inferring the connection.
    """
    weather = farm.current_weather
    humid = weather.humidity_pct is not None and weather.humidity_pct >= 70
    wet = weather.rainfall_recent_mm is not None and weather.rainfall_recent_mm >= 20

    causes = list(category.likely_causes.items())

    def sort_key(item: tuple[str, str]) -> int:
        cause = item[0]
        if (humid or wet) and cause in _HUMID_BOOSTED_CAUSES:
            return 0
        if not (humid or wet) and cause in _DRY_BOOSTED_CAUSES:
            return 0
        return 1

    causes.sort(key=sort_key)
    return causes


def weather_matches_trigger(trigger: WeatherTrigger, farm: FarmProfile) -> bool:
    """True if the active farm's current weather satisfies every threshold a
    disease's WeatherTrigger actually sets. A threshold left as None on the
    trigger is not checked -- e.g. a trigger with only min_humidity_pct set
    ignores temperature entirely, rather than treating an unset field as
    "any weather is fine" for that field once at least one field matches.

    Only diseases whose NamedDisease.weather_trigger is not None are ever
    checked here -- see get_weather_relevant_diseases, and the module
    docstring on WeatherTrigger for why an unset trigger means "weather is
    deliberately left out of this diagnosis" rather than "assume it applies".
    """
    weather = farm.current_weather
    if trigger.min_humidity_pct is not None:
        if weather.humidity_pct is None or weather.humidity_pct < trigger.min_humidity_pct:
            return False
    if trigger.min_recent_rainfall_mm is not None:
        if weather.rainfall_recent_mm is None or weather.rainfall_recent_mm < trigger.min_recent_rainfall_mm:
            return False
    if trigger.min_temp_c is not None:
        if weather.temp_c is None or weather.temp_c < trigger.min_temp_c:
            return False
    if trigger.max_temp_c is not None:
        if weather.temp_c is None or weather.temp_c > trigger.max_temp_c:
            return False
    return True


def get_control_for_region(disease: NamedDisease, country_code: str) -> list[RegionalControl]:
    """Select which of a disease's RegionalControl entries to tell this
    farmer about: every universal entry (country_codes empty -- general
    agronomic practice with no region restriction), plus any region-specific
    entry whose country_codes includes this farmer's country.

    Deliberately never defaults to any one country's regional advice when
    country_code is unknown ("") or doesn't match -- a region-specific entry
    (e.g. a named fungicide product or variety sourced for one country) is
    only surfaced to farmers actually in that country. This keeps the agent
    worldwide-neutral: no region is treated as the default, including where
    most of the current source material happens to originate from.
    """
    return [
        entry
        for entry in disease.control
        if not entry.country_codes or (country_code and country_code in entry.country_codes)
    ]


@dataclass
class PlantSession:
    """Holds state across one multi-turn "Hey Plant" conversation."""

    crop: str | None = None
    initial_symptom_text: str = ""
    matched_category: str | None = None
    answers: list[str] = field(default_factory=list)
    questions_asked: list[FollowUpQuestion] = field(default_factory=list)
    done: bool = False
    abiotic_hint: bool = False
    _farm: FarmProfile | None = field(default=None, repr=False)

    def _remaining_questions(self) -> list[FollowUpQuestion]:
        if self.matched_category is None:
            return []
        category = SYMPTOM_CATEGORIES[self.matched_category]
        return [q for q in category.follow_up_questions if q not in self.questions_asked]

    def start(self, symptom_text: str, crop: str | None = None) -> str:
        """Begin the conversation with the farmer's initial symptom report."""
        self.initial_symptom_text = symptom_text
        self.crop = crop.lower() if crop else None
        self.matched_category = match_symptom_category(symptom_text)
        if has_abiotic_hint(symptom_text):
            self.abiotic_hint = True

        if self.matched_category is None:
            self.done = True
            return (
                "I couldn't quite match that to a symptom I recognize. Could you describe "
                "it differently -- for example, is it wilting, spotted, yellowing, or "
                "discolored leaves?"
            )

        remaining = self._remaining_questions()
        if not remaining or len(self.questions_asked) >= MAX_FOLLOW_UPS:
            return self._final_diagnosis()

        question = remaining[0]
        self.questions_asked.append(question)
        return self._phrase_question(question)

    def respond(self, answer_text: str) -> str:
        """Feed the farmer's answer to the last follow-up question.

        Handles simple correction: if the answer looks like a correction
        to the original symptom rather than an answer to the question
        (e.g. "no wait, it's the leaves not the stem"), re-run matching
        instead of forcing it into the question flow.
        """
        if self.done:
            return "This diagnosis is already complete. Say the wake word again to start a new one."

        correction_markers = ("no wait", "actually", "i mean", "sorry i meant", "correction")
        if any(marker in answer_text.lower() for marker in correction_markers):
            return self.start(answer_text, crop=self.crop)

        if has_abiotic_hint(answer_text):
            self.abiotic_hint = True

        self.answers.append(answer_text)

        remaining = self._remaining_questions()
        if not remaining or len(self.questions_asked) >= MAX_FOLLOW_UPS:
            return self._final_diagnosis()

        question = remaining[0]
        self.questions_asked.append(question)
        return self._phrase_question(question)

    def _phrase_question(self, question: FollowUpQuestion) -> str:
        try:
            return llm_client.generate(
                "Rephrase this follow-up question for a farmer in one short, natural "
                f"spoken sentence, keeping the same meaning exactly:\n\n{question.prompt}"
            )
        except RuntimeError:
            return question.prompt

    def _final_diagnosis(self) -> str:
        self.done = True
        category = SYMPTOM_CATEGORIES[self.matched_category]

        causes = (
            weather_adjusted_causes(category, self._farm)
            if self._farm is not None
            else list(category.likely_causes.items())
        )

        named: list[NamedDisease] = []
        if self.crop:
            named = [d for d in get_named_diseases(self.crop) if d.symptom_category == self.matched_category]

        summary_lines = [
            f"Symptom category: {category.name} ({category.description})",
            "Likely causes, in order of likelihood given current conditions:",
        ]
        for cause, explanation in causes:
            summary_lines.append(f"  - {cause}: {explanation}")

        if named:
            summary_lines.append("Specific diseases matching this symptom on this crop:")
            country_code = self._farm.country_code if self._farm is not None else ""
            for disease in named:
                line = f"  - {disease.name} ({disease.scientific_name}): {disease.symptoms}"

                # Region-aware control selection: universal advice always
                # shows; a region-specific entry (named product/variety)
                # only shows when the farmer's country actually matches --
                # see get_control_for_region's docstring for why unknown/
                # non-matching regions never fall back to any one country's
                # advice by default.
                applicable_control = get_control_for_region(disease, country_code)
                control_parts = []
                for entry in applicable_control:
                    if entry.country_codes:
                        control_parts.append(f"{entry.text} (regional advice for {entry.region_label})")
                    else:
                        control_parts.append(entry.text)
                line += " Control: " + " ".join(control_parts)

                # Only mention weather for a disease when we actually have
                # sourced trigger data for it -- see WeatherTrigger's
                # docstring in plant_data.py. Diseases with no trigger data
                # get no weather commentary at all, rather than a guessed one.
                if disease.weather_trigger is not None and self._farm is not None:
                    if weather_matches_trigger(disease.weather_trigger, self._farm):
                        line += f" Current weather matches this disease's known risk conditions ({disease.weather_trigger.description})."
                    else:
                        line += f" Current weather does not match this disease's known risk conditions ({disease.weather_trigger.description})."
                summary_lines.append(line)

        answers_text = "; ".join(self.answers) if self.answers else "(no follow-up answers given)"
        summary_lines.append(f"Farmer's answers to follow-up questions: {answers_text}")

        if self.abiotic_hint:
            summary_lines.append(
                "Caveat: the farmer's description suggests this might not be a disease at "
                "all -- e.g. it may affect unrelated plants nearby, not be spreading, have "
                "a sharp boundary, or trace to water/fertilizer/chemical exposure rather "
                "than a pathogen. Consider ruling out a nonliving cause before treating "
                "for disease."
            )

        deterministic_summary = "\n".join(summary_lines)

        prompt = (
            "You are an agronomist advisor speaking to a farmer over voice, concluding "
            "a diagnostic conversation about a plant health problem. Based ONLY on the "
            "deterministic assessment below, give a short spoken diagnosis (3-5 sentences): "
            "state the most likely cause first, mention the current weather's role if "
            "relevant, and give one practical next step. Do not invent facts beyond what's "
            "given. If a caveat about a possible nonliving cause is present, mention it "
            "clearly rather than glossing over it.\n\n"
            f"Initial symptom described: {self.initial_symptom_text}\n\n"
            f"Assessment:\n{deterministic_summary}"
        )
        try:
            return llm_client.generate(prompt)
        except RuntimeError:
            return deterministic_summary

    def set_farm(self, farm: FarmProfile) -> None:
        """Attach the active farm so _final_diagnosis can weigh
        causes by current weather (see weather_adjusted_causes)."""
        self._farm = farm


class PlantAgent:
    """Entry point used by main.py: creates/continues PlantSession objects."""

    def __init__(self) -> None:
        self._active_sessions: dict[str, PlantSession] = {}

    def handle(self, farm: FarmProfile, transcript: str, crop: str | None = None, session_id: str = "default") -> str:
        """Drive one turn of a diagnostic conversation.

        `session_id` lets main.py track multiple concurrent conversations
        if ever needed; a single voice agent normally only has one active
        session at a time (session_id="default" is fine).
        """
        session = self._active_sessions.get(session_id)

        if session is None or session.done:
            session = PlantSession()
            session.set_farm(farm)
            self._active_sessions[session_id] = session
            response = session.start(transcript, crop=crop)
        else:
            response = session.respond(transcript)

        if session.done and session.matched_category is not None:
            category_name = session.matched_category
            top_cause = weather_adjusted_causes(SYMPTOM_CATEGORIES[category_name], farm)[0][0]
            farm.add_symptom_report(
                crop=session.crop or "unspecified",
                symptoms=session.initial_symptom_text,
                diagnosis=f"{category_name} (likely cause: {top_cause})",
            )

        return response

    def is_done(self, session_id: str = "default") -> bool:
        """True if the named conversation has reached a final diagnosis
        (or has no active turns yet), i.e. it's safe to stop streaming ASR
        audio into it and return to wakeword listening."""
        session = self._active_sessions.get(session_id)
        return session is None or session.done
