"""Cross-domain intent detection, shared by the farmer dashboard's chat and
the voice pipeline's combined "Hey Green" wakeword.

Originally built only for the farmer dashboard (no wakeword there -- the
farmer types/speaks freely, so something has to catch "what should I
plant" arriving while a Weather-routed reply was still last-active). The
voice pipeline (main.py) used to need none of this, since each of its
three wakewords ("Hey Weather"/"Hey Crop"/"Hey Plant") picked the domain
directly. That's no longer true for Weather/Crop specifically: they were
merged into one wakeword -- originally spoken as "Hey Field", now "Hey
Green" (2026-09-23), the underlying merged-domain concept and the
`resolve_field_domain()` function name never changed, only the phrase --
see wakeword/router.py and main.py's `resolve_field_domain()`, covering
the many everyday farm questions that don't cleanly sort into "obviously
weather" or "obviously crop" before the farmer has even spoken -- "Hey
Green" fires, THEN the transcript is routed via detect_domain() same as
dashboard chat. "Hey Doc" (the plant-diagnosis wakeword; internally still
the "plant" domain) stays its own separate wakeword (a different
conversation shape -- multi-turn diagnosis needs a symptom description,
not a one-shot question -- so it was kept apart rather than folded in
too).

Keyword matching is the first and fast path. Only when no keyword matches
does classify_with_llm() ask the model for a single constrained label
(weather / crop / plant / unclear), given the last few turns so follow-ups
like "and tomorrow?" still land correctly. "unclear" -- or no model
available -- means the caller asks the farmer to repeat instead of guessing
a domain. Only ever suggests a redirect; the caller decides whether to act on
it, and it must never fire mid-conversation (see farmer_server.py's
guard against running this on a Plant follow-up answer, where a farmer's
short reply like "the whole plant" carries none of these keywords anyway
but could coincidentally overlap one in principle).
"""

from __future__ import annotations

import re

from . import llm_client

_CLASSIFIER_SYSTEM = "You are a strict text classifier. Reply with exactly one lowercase word and nothing else."

# Checked in dict order, first match wins -- most specific domain first.
# Symptom words are unambiguous, and crop questions routinely mention
# weather context ("which crop suits this hot weather") while weather
# questions rarely mention crops, so plant > crop > weather. Weather used
# to be checked first, which sent every crop question that mentioned rain
# or heat to Weather.
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "plant": [
        "wilting", "wilt", "wither", "withered", "withering", "yellowing",
        "yellow leaves", "spots on", "leaf spot", "disease", "sick", "dying",
        "dead leaves", "rotting", "rot", "mold", "mould", "mildew", "pest",
        "infected", "infection", "fungus", "blight", "curling",
        "looks wrong", "something wrong", "not looking right",
        "turning brown", "falling off", "wrong with my",
    ],
    "crop": [
        "what should i plant", "what should i grow", "what to plant",
        "what to grow", "suitable to plant", "good to plant", "good crop",
        "which crop", "what crop", "plant now", "grow now", "planting season",
        "suitable crop", "recommend a crop", "should i grow",
        # Bare words -- ASR regularly mangles the start of a question
        # ("what crops" came back as "But crops I have"), so full-phrase
        # matches alone missed real crop questions.
        "crop", "grow", "planting", "harvest", "sow", "sowing", "seed",
        "cultivate",
    ],
    "weather": [
        "weather", "forecast", "rain", "raining", "rainfall", "temperature",
        "humid", "humidity", "hot", "cold", "sunny", "sunshine", "storm",
        "wind", "windy", "climate", "degrees",
    ],
}


def detect_domain(text: str) -> str | None:
    """Return the domain a message's own words most clearly point to, or
    None if nothing matches strongly enough to suggest a redirect.

    Deliberately conservative: a message with no matching keywords (e.g.
    "yes", "the whole plant", "thanks") returns None rather than guessing,
    so a genuine mid-conversation follow-up answer is never misrouted.
    """
    lowered = text.lower()
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            # REAL BUG FOUND AND FIXED (2026-09-27, reported live: "what is
            # crop rotation" got routed to plant): plain substring matching
            # ("rot" in "rotation") false-matched single-word keywords
            # inside unrelated longer words. Word-boundary matching fixes
            # this for both single- and multi-word keywords (a space in a
            # multi-word phrase already acted as an implicit boundary, so
            # this doesn't change those).
            if re.search(r"\b" + re.escape(keyword) + r"\b", lowered):
                return domain
    return None


def classify_with_llm(text: str, recent_turns: str = "") -> str | None:
    """Fallback for messages no keyword matched. Returns "weather", "crop",
    "plant", "general", or None when the message is truly unclear (cut off,
    garbled, the assistant's own words echoed back) or no model is
    available -- the caller should then ask the farmer to repeat.

    "general" (added 2026-09-27, in response to a live report: a farming
    question outside all three specialists -- "how often should I water
    tomatoes", "what's crop rotation" -- used to have nowhere to land here
    but "unclear", so it fell straight to the generic "sorry, I didn't
    catch that" instead of actually being answerable. Routes to
    domains/general.py's GeneralAgent -- the one deliberate exception to
    this project's "deterministic logic, LLM only phrases" rule, since an
    open-ended farming question has no fixed dataset to phrase from.
    "unclear" is reserved for messages that aren't a real farming question
    at all, not ones that are just outside these four."""
    context = f"Recent conversation:\n{recent_turns}\n\n" if recent_turns else ""
    prompt = (
        "A farm voice assistant has four specialists:\n"
        "weather - weather conditions or forecasts: rain, temperature, wind, humidity, any day\n"
        "crop - what to plant or grow, crop suitability, planting or harvest timing, "
        "general crop care like watering, spacing or fertiliser\n"
        "plant - a sick or damaged plant: symptoms, pests, diseases\n"
        "general - any other genuine farming question that isn't specifically about "
        "current/forecast weather, which crop to grow, or a sick plant\n\n"
        "Classify the farmer's latest message. Use the recent conversation to understand "
        "short follow-ups like 'and tomorrow?'. Answer unclear if the message is cut off, "
        "garbled, not a farming question at all, or sounds like the assistant talking.\n\n"
        f"{context}Latest message: \"{text}\"\n\n"
        "Answer with one word: weather, crop, plant, general, or unclear."
    )
    try:
        raw = llm_client.generate(prompt, system_instruction=_CLASSIFIER_SYSTEM)
    except RuntimeError:
        return None
    word = re.sub(r"[^a-z]", "", raw.strip().lower().split()[0]) if raw.strip() else ""
    return word if word in ("weather", "crop", "plant", "general") else None


def suggest_redirect(text: str, active_domain: str) -> str | None:
    """If `text` clearly belongs to a different domain than the one
    currently active, return that domain's name; otherwise None.

    Only called on the FIRST message of a fresh exchange for the active
    domain -- see farmer_server.py. A message that matches no domain, or
    matches the domain already active, is not a redirect.
    """
    detected = detect_domain(text)
    if detected is not None and detected != active_domain:
        return detected
    return None


def resolve_field_domain(text: str) -> str:
    """Resolve a "Hey Green" utterance to "weather" or "crop" -- see this
    module's docstring. Never returns "plant" (that keeps its own separate
    wakeword) and never returns None (unlike detect_domain/suggest_redirect,
    "Hey Green" already committed to being answered by ONE of these two
    domains the moment the wakeword fired, so ambiguous wording still needs
    a decision, not a non-answer).

    Defaults to "weather" when nothing matches -- an open-ended check-in
    like "how's it going" or "what's happening out there" reads more like a
    conditions question than a planting one, and Weather's answer is also
    the input Crop's own suitability scoring depends on, so it's the safer
    unsure-what-they-meant default of the two.
    """
    detected = detect_domain(text)
    if detected in ("weather", "crop"):
        return detected
    return "weather"
