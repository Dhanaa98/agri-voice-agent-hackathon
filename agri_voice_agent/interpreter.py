"""Context-aware interpretation for messages the fast deterministic paths
(farm-command regexes, domain keywords) couldn't place.

Replaces a single-word domain classifier whose only fallback was a fixed
"Sorry, I didn't catch that" -- which failed on anything conversational:
"let's focus on the farm in Zurich", "and tomorrow?", or ASR-mangled speech
("the format" for "the farm") that is obvious from the previous turns.

One LLM call returns a structured action. Only NON-destructive actions are
possible here (answer, route to a domain, select or add a farm); deleting,
renaming and relocating a farm stay regex-only in farmer_server.py so a
misread can never destroy data.
"""

from __future__ import annotations

import json
import re

from . import llm_client

ACTIONS = {"weather", "crop", "plant", "select_farm", "add_farm", "answer", "unclear"}

_SYSTEM = (
    "You interpret messages for a farm voice assistant and reply only with a JSON object. "
    "Messages come from speech recognition and may contain misheard words -- use the "
    "conversation and the farm list to work out what the farmer most likely meant."
)


def interpret(text: str, history: list[tuple[str, str]], farms: list[tuple[str, str]], active_farm: str | None) -> dict:
    """Returns a dict with an "action" from ACTIONS plus action-specific keys:
      weather/crop/plant -- "question": the message rewritten to stand alone
                            using context ("and tomorrow?" -> "will it rain
                            tomorrow?"), optional "farm"
      select_farm        -- "farm": a name from `farms`
      add_farm           -- optional "name", "location"
      answer / unclear   -- "reply": what to say back
    Raises RuntimeError when no model is available."""
    farm_lines = "\n".join(f"- {n} ({loc or 'no location set'})" for n, loc in farms) or "(no farms yet)"
    convo = "\n".join(f"{role}: {t}" for role, t in history[-10:]) or "(start of conversation)"
    prompt = (
        f"Farmer's farms:\n{farm_lines}\n"
        f"Farm currently in focus: {active_farm or 'none'}\n\n"
        f"Recent conversation:\n{convo}\n\n"
        f'Latest message: "{text}"\n\n'
        "Choose one action:\n"
        '- "weather": about weather or forecasts\n'
        '- "crop": what to plant, crop suitability, or how to grow a crop\n'
        '- "plant": a sick or damaged plant (symptoms, pests, disease)\n'
        '- "select_farm": the farmer wants to switch to / focus on / talk about one of their farms\n'
        '- "add_farm": the farmer wants to add or create a new farm\n'
        '- "answer": anything else you can reply to sensibly -- a general farming question, a '
        "follow-up about something said earlier, a question about the conversation or their farms, "
        "or small talk\n"
        '- "unclear": the message is too garbled to guess at even with context\n\n'
        "JSON keys:\n"
        '"action": one of the above.\n'
        '"question": for weather/crop/plant, the farmer\'s request rewritten to make sense on its own '
        "using the conversation.\n"
        '"farm": for select_farm (required) or weather/crop/plant (only if they named one), the exact '
        "farm name from the list above. Match loosely -- a location or a misheard name counts.\n"
        '"name": for add_farm, ONLY if the farmer explicitly named the farm (e.g. "called North '
        'Field"); otherwise an empty string. Never use the location or "New Farm" as a name.\n'
        '"location": for add_farm, the place they said the farm is in, or an empty string.\n'
        '"reply": for answer or unclear. Spoken style, 1-4 short sentences, no lists. For unclear, '
        "ask a specific question about what you think they meant rather than just asking them to "
        "repeat. Never invent facts about their farms beyond the list above."
    )
    raw = llm_client.generate(prompt, system_instruction=_SYSTEM, json_mode=True)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    try:
        result = json.loads(match.group(0) if match else raw)
    except (json.JSONDecodeError, AttributeError):
        return {"action": "unclear"}
    if not isinstance(result, dict) or result.get("action") not in ACTIONS:
        return {"action": "unclear"}
    return result
