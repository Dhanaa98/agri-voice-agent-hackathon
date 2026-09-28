"""Plant disease diagnostic conversation agent -- reached via "Hey Green"
(routed here like any other domain, see intent.py's resolve_field_domain();
no longer has its own separate wakeword as of 2026-09-28, previously
"Hey Doc").

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
main.py is responsible for creating one when "Hey Green" resolves to the
"plant" domain and feeding it each ASR transcript in turn until it
reports done.
"""

from __future__ import annotations

import json
import re
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
    detect_crop,
    get_named_diseases,
)

# Without the LLM the doctor falls back to the fixed per-category questions,
# of which each category has two.
MAX_FOLLOW_UPS = 2

# With the LLM: keep asking until one candidate clearly leads, up to this many
# questions. "Clearly leads" is a deterministic rule on the normalised
# likelihoods, not the model's own say-so.
MAX_QUESTIONS = 5
CONFIDENT_LIKELIHOOD = 0.7
CONFIDENT_MARGIN = 0.25
# Diagnose straight from the first description, with no questions, only when
# it is this unambiguous (e.g. the farmer names the textbook symptoms).
NO_QUESTION_LIKELIHOOD = 0.9

NOT_A_DISEASE = "Not a disease (watering, nutrient, weather or chemical damage)"
UNLISTED = "Something not listed here"
ASK_CROP_QUESTION = "Which crop or plant is this happening on?"
ASK_SYMPTOM_QUESTION = (
    "What exactly do you see on the plant -- spots, yellowing, wilting, curled leaves, "
    "a powdery or fuzzy mould, or rotting?"
)
UNRECOGNISED_TEXT = (
    "I couldn't quite match that to a symptom I recognize. Could you describe "
    "it differently -- for example, is it wilting, spotted, yellowing, or "
    "discolored leaves?"
)

_ASSESS_SYSTEM = (
    "You are a careful plant pathologist helping diagnose a crop problem by voice. "
    "Reply with a single JSON object and nothing else."
)

# Words too common in symptom text to tell diseases apart.
_GENERIC_WORDS = {
    "leaf", "leaves", "plant", "plants", "have", "with", "that", "this", "they", "from", "there",
    "then", "some", "into", "also", "more", "when", "which", "their", "them", "were", "been",
    "mostly", "very", "just", "like", "looks", "look", "getting", "turning", "become", "becomes",
}


def _symptom_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 3 and w not in _GENERIC_WORDS}


def _parse_json_object(raw: str) -> dict | None:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group(0))
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def rank_named_diseases(crop: str, category: str | None, description: str, limit: int = 4) -> list[NamedDisease]:
    """The crop's named diseases that fit the farmer's description, best
    match first. A disease qualifies if it's in the matched symptom category
    or its documented symptoms share at least two distinctive words with
    what the farmer said -- the keyword category alone is too coarse
    ("dark oily blotches with white mould" matched leaf_spot, which used to
    hide late blight, filed under drying_blight). Capped at four so the
    LLM prompt stays small."""
    said = _symptom_words(description)
    scored = []
    for disease in get_named_diseases(crop):
        overlap = len(said & _symptom_words(f"{disease.name} {disease.symptoms}"))
        in_category = disease.symptom_category == category
        # With no symptom category yet, every disease on the crop stays in
        # play and word overlap alone orders them.
        if category is None or in_category or overlap >= 2:
            scored.append((overlap + (1 if in_category else 0), disease))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [disease for _, disease in scored[:limit]]

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
    # Powdery and downy mildews are filed as leaf_spot (see "mildew" above);
    # farmers usually describe them by what they see instead.
    "powder": "leaf_spot",
    "mould": "leaf_spot",
    "mold": "leaf_spot",
    "fuzz": "leaf_spot",
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
    """Holds state across one multi-turn plant-diagnosis conversation."""

    crop: str | None = None
    initial_symptom_text: str = ""
    matched_category: str | None = None
    answers: list[str] = field(default_factory=list)
    # The questions actually put to the farmer, in order (answers[i] replies
    # to questions_asked[i]).
    questions_asked: list[str] = field(default_factory=list)
    done: bool = False
    abiotic_hint: bool = False
    # Latest normalised candidate -> likelihood from _assess(), best first.
    likelihoods: dict[str, float] = field(default_factory=dict)
    _farm: FarmProfile | None = field(default=None, repr=False)

    @property
    def top_candidate(self) -> str | None:
        return next(iter(self.likelihoods), None)

    def _static_questions_left(self) -> list[FollowUpQuestion]:
        if self.matched_category is None:
            return []
        category = SYMPTOM_CATEGORIES[self.matched_category]
        return [q for q in category.follow_up_questions if q.prompt not in self.questions_asked]

    def _ask(self, question: str) -> str:
        self.questions_asked.append(question)
        return question

    def start(self, symptom_text: str, crop: str | None = None) -> str:
        """Begin the conversation with the farmer's initial symptom report."""
        self.initial_symptom_text = symptom_text
        self.crop = crop.lower() if crop else None
        self.matched_category = match_symptom_category(symptom_text)
        if has_abiotic_hint(symptom_text):
            self.abiotic_hint = True

        return self._next_turn()

    def _next_turn(self) -> str:
        """Ask the next question, or diagnose once one candidate clearly
        leads -- after as few as one question, at most MAX_QUESTIONS."""
        # A vague opening ("something's wrong with my tomatoes") is exactly
        # when questions help most, so ask what they see rather than give up.
        if self.matched_category is None and ASK_SYMPTOM_QUESTION not in self.questions_asked:
            return self._ask(ASK_SYMPTOM_QUESTION)
        # Knowing the crop is what unlocks the named-disease entries, so it's
        # worth one question when the farmer didn't say.
        if self.crop is None and ASK_CROP_QUESTION not in self.questions_asked:
            return self._ask(ASK_CROP_QUESTION)
        # Still no recognisable symptom and no crop entries to fall back on.
        if self.matched_category is None and not (self.crop and get_named_diseases(self.crop)):
            self.done = True
            return UNRECOGNISED_TEXT

        assessment = self._assess()
        if assessment is None:
            # No LLM available: the original fixed two-question flow.
            remaining = self._static_questions_left()
            static_asked = sum(1 for q in self.questions_asked if q not in (ASK_CROP_QUESTION, ASK_SYMPTOM_QUESTION))
            if not remaining or static_asked >= MAX_FOLLOW_UPS:
                return self._final_diagnosis()
            return self._ask(remaining[0].prompt)

        self.likelihoods, next_question = assessment
        ranked = list(self.likelihoods.values())
        top = ranked[0]
        runner_up = ranked[1] if len(ranked) > 1 else 0.0
        confident = top >= CONFIDENT_LIKELIHOOD and top - runner_up >= CONFIDENT_MARGIN
        if confident and (self.answers or top >= NO_QUESTION_LIKELIHOOD):
            return self._final_diagnosis()
        if len(self.questions_asked) >= MAX_QUESTIONS:
            return self._final_diagnosis()
        if not next_question or next_question in self.questions_asked:
            return self._final_diagnosis()
        return self._ask(next_question)

    def _candidates(self) -> list[tuple[str, str]]:
        """The options the assessment may choose between -- this crop's own
        knowledge-base diseases that fit the description (or, with no crop
        entries, the symptom category's broad causes), plus "not a disease"
        and "something not listed" so a poor fit is never forced onto a
        named disease."""
        described = " ".join([self.initial_symptom_text, *self.answers])
        options: list[tuple[str, str]] = []
        if self.crop:
            options = [
                (d.name, d.symptoms)
                for d in rank_named_diseases(self.crop, self.matched_category, described, limit=6)
            ]
        if not options and self.matched_category:
            options = [
                (f"{cause.replace('_', ' ')} problem", why)
                for cause, why in SYMPTOM_CATEGORIES[self.matched_category].likely_causes.items()
                if cause != "physical"
            ]
        options.append((NOT_A_DISEASE, "watering, drainage, nutrient shortage, heat/cold or chemical/herbicide damage; usually affects plants evenly or several kinds of plant and doesn't spread"))
        options.append((UNLISTED, "none of the other options fits the description well"))
        return options

    def _assess(self) -> tuple[dict[str, float], str | None] | None:
        """Ask the LLM how likely each candidate is given the conversation so
        far, and which single question would best separate the leaders.
        Returns (likelihoods best-first, next question), or None when no LLM
        is available or its reply can't be used."""
        options = self._candidates()
        option_lines = "\n".join(f"- {name}: {looks_like}" for name, looks_like in options)
        conversation = [f"Farmer's first description: {self.initial_symptom_text}"]
        for question, answer in zip(self.questions_asked, self.answers):
            conversation.append(f"Asked: {question}")
            conversation.append(f"Farmer answered: {answer}")
        farm_context = self._farm.to_prompt_context() if self._farm is not None else "unknown"
        prompt = (
            f"Crop: {self.crop or 'unknown'}\n"
            f"Farm and weather: {farm_context}\n\n"
            f"Candidates (use these exact names only):\n{option_lines}\n\n"
            "Conversation so far:\n" + "\n".join(conversation) + "\n\n"
            "Score how likely each candidate is from the farmer's evidence only; give low scores "
            "to anything the answers contradict. Then write the ONE short, plain question a farmer "
            "could answer just by looking at the plant that would best tell the top candidates apart. "
            "Never ask about the same feature twice: if the farmer couldn't answer a question, switch "
            "to a different, easier-to-check sign (which leaves or parts, how fast it spread, recent "
            "weather, other plants affected, roots or stems, smell or ooze).\n\n"
            'Reply as JSON: {"likelihoods": {"<candidate name>": <0 to 1>, ...}, "next_question": "<question>"}'
        )
        try:
            raw = llm_client.generate(prompt, system_instruction=_ASSESS_SYSTEM)
        except RuntimeError:
            return None
        data = _parse_json_object(raw)
        if data is None or not isinstance(data.get("likelihoods"), dict):
            return None

        by_lower = {name.lower(): name for name, _ in options}
        scores: dict[str, float] = {}
        for key, value in data["likelihoods"].items():
            name = by_lower.get(str(key).strip().lower())
            if name is not None and isinstance(value, (int, float)) and value > 0:
                scores[name] = float(value)
        total = sum(scores.values())
        if total <= 0:
            return None
        ranked = dict(sorted(((n, s / total) for n, s in scores.items()), key=lambda p: p[1], reverse=True))
        question = data.get("next_question")
        question = question.strip() if isinstance(question, str) and question.strip() else None
        return ranked, question

    def respond(self, answer_text: str) -> str:
        """Feed the farmer's answer to the last follow-up question.

        Handles simple correction: if the answer looks like a correction
        to the original symptom rather than an answer to the question
        (e.g. "no wait, it's the leaves not the stem"), re-run matching
        instead of forcing it into the question flow.
        """
        if self.done:
            return "This diagnosis is already complete. Say the wake word again to start a new one."

        # Only unmistakable restarts -- "actually" and "I mean" turn up in
        # ordinary answers too, and would throw away every answer so far.
        correction_markers = ("no wait", "sorry i meant", "correction", "start again", "start over")
        if any(marker in answer_text.lower() for marker in correction_markers):
            return self.start(answer_text, crop=self.crop)

        if has_abiotic_hint(answer_text):
            self.abiotic_hint = True

        self.answers.append(answer_text)
        if self.crop is None:
            self.crop = detect_crop(answer_text)
        if self.matched_category is None:
            self.matched_category = match_symptom_category(answer_text)

        return self._next_turn()

    def _final_diagnosis(self) -> str:
        self.done = True
        if self.matched_category is None:
            # The farmer never used a recognised symptom word, but a crop
            # disease was identified -- use that disease's own category.
            top = next((d for d in get_named_diseases(self.crop or "") if d.name == self.top_candidate), None)
            if top is None:
                return UNRECOGNISED_TEXT
            self.matched_category = top.symptom_category
        category = SYMPTOM_CATEGORIES[self.matched_category]

        causes = (
            weather_adjusted_causes(category, self._farm)
            if self._farm is not None
            else list(category.likely_causes.items())
        )

        named: list[NamedDisease] = []
        if self.crop:
            description = " ".join([self.initial_symptom_text, *self.answers])
            named = rank_named_diseases(self.crop, self.matched_category, description, limit=6)
            if self.likelihoods:
                # Order by the conversation's assessment, and drop diseases
                # the farmer's answers effectively ruled out.
                named = [d for d in named if self.likelihoods.get(d.name, 0) >= 0.1] or named
                named.sort(key=lambda d: self.likelihoods.get(d.name, 0), reverse=True)
            named = named[:4]

        summary_lines = [
            f"Symptom category: {category.name} ({category.description})",
            "Broad cause categories for this symptom (background), weather-weighted:",
        ]
        for cause, explanation in causes:
            summary_lines.append(f"  - {cause}: {explanation}")

        if self.likelihoods:
            # Only real contenders -- a 5% "not a disease" otherwise gets
            # read out as a caveat on a clear diagnosis.
            contenders = [(n, s) for n, s in self.likelihoods.items() if s >= 0.15][:3]
            ranked = ", ".join(f"{name} ({share:.0%})" for name, share in contenders)
            summary_lines.append(
                f"Assessment from the farmer's answers ({len(self.questions_asked)} questions asked): {ranked}"
            )
            shares = list(self.likelihoods.values())
            clear_leader = shares[0] >= CONFIDENT_LIKELIHOOD and shares[0] - (shares[1] if len(shares) > 1 else 0) >= CONFIDENT_MARGIN
            if not clear_leader:
                summary_lines.append(
                    "The answers did NOT clearly separate the top candidates: present the top two as "
                    "possibilities rather than a firm diagnosis, give the control steps that suit both, and "
                    "suggest a closer look at the leaves or showing a sample to a local extension officer."
                )
            if self.top_candidate == NOT_A_DISEASE:
                summary_lines.append(
                    "The answers point away from a disease: explain the likely watering, nutrient, weather "
                    "or chemical cause instead of recommending fungicide."
                )
            elif self.top_candidate == UNLISTED:
                summary_lines.append(
                    "None of the known diseases fits clearly: say so honestly, give the broad likely cause, "
                    "and suggest showing a sample to a local extension officer or plant clinic."
                )

        if named:
            summary_lines.append(
                "Specific diseases on this crop that fit the description, most likely first:"
            )
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

        if self.answers:
            summary_lines.append("Follow-up questions and the farmer's answers:")
            for question, answer in zip(self.questions_asked, self.answers):
                summary_lines.append(f"  - Q: {question} A: {answer}")
        else:
            summary_lines.append("No follow-up questions were needed.")

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
            "Conclude this plant-health diagnosis with a 3-5 sentence spoken answer, "
            "based only on the assessment below. If specific diseases are listed, name the "
            "most likely one (the first listed, which the farmer's answers support best) -- "
            "unless the assessment says the answers didn't separate them, in which case be "
            "honest that it's one of the top two. "
            "Mention the current weather's "
            "role if relevant. Then give the control steps listed for that disease, including "
            "any product, dose or regional advice given -- don't swap in advice that isn't "
            "listed, and say it as plain advice without reading out source or region names. "
            "The broad cause list is background only: mention a non-disease cause (watering, "
            "nutrients, chemicals) only if a 'Caveat' line is present or the assessment points "
            "away from a disease.\n\n"
            f"Farm context:\n{self._farm.to_prompt_context() if self._farm is not None else 'unknown'}\n\n"
            f"{self._farm.recent_chat_context('plant') if self._farm is not None else ''}\n\n"
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
            # Voice and chat never pass a crop explicitly, so take it from the
            # farmer's own words -- without this, named diseases were never
            # consulted outside the manual tests.
            response = session.start(transcript, crop=crop or detect_crop(transcript))
        else:
            response = session.respond(transcript)

        if session.done and session.matched_category is not None:
            category_name = session.matched_category
            top_cause = weather_adjusted_causes(SYMPTOM_CATEGORIES[category_name], farm)[0][0]
            identified = session.top_candidate
            if identified and identified not in (NOT_A_DISEASE, UNLISTED):
                diagnosis = f"{identified} ({category_name})"
            else:
                diagnosis = f"{category_name} (likely cause: {top_cause})"
            farm.add_symptom_report(
                crop=session.crop or "unspecified",
                symptoms=session.initial_symptom_text,
                diagnosis=diagnosis,
            )

        return response

    def abandon(self, session_id: str = "default") -> None:
        """Drop an in-progress diagnostic session without finishing it --
        called when the farmer's own words clearly redirect to a different
        domain mid-conversation (e.g. "how is the weather" partway through
        a symptom Q&A). Without this, the next plant-diagnosis call would
        see session.done still False and silently resume the abandoned
        conversation instead of starting a fresh one."""
        self._active_sessions.pop(session_id, None)

    def is_done(self, session_id: str = "default") -> bool:
        """True if the named conversation has reached a final diagnosis
        (or has no active turns yet), i.e. it's safe to stop streaming ASR
        audio into it and return to wakeword listening."""
        session = self._active_sessions.get(session_id)
        return session is None or session.done
