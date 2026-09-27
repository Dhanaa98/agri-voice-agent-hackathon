"""General farming Q&A fallback agent -- not a wakeword/keyword domain like
Weather/Crop/Plant, only ever reached via classify_with_llm() returning
"general" (see intent.py) when a farmer's message is clearly a farming
question but doesn't fit weather conditions, crop suitability, or a sick
plant specifically ("how often should I water tomatoes", "what's crop
rotation", "why are my seedlings leggy").

Unlike the other three domains, there is no deterministic data behind this
one -- there's no fixed dataset to score an open-ended question against,
so the LLM is the whole answer here, not just the phrasing layer. Kept
deliberately narrow (a system instruction that steers it back to farming,
short answers, no invented specifics about THIS farm) rather than a
general-purpose chatbot, since the project's philosophy elsewhere is
"deterministic logic, LLM only phrases" -- this is the one intentional
exception, for the one class of question that has no deterministic
grounding to phrase from.
"""

from __future__ import annotations

from .. import llm_client
from ..farm_state import FarmProfile

_SYSTEM_INSTRUCTION = (
    "You are a warm, experienced farm advisor talking to a farmer over voice, "
    "not writing a report. Speak like you're standing in the field with them: "
    "plain words, contractions, short sentences, 2-4 sentences total. Never "
    "list bullet points or headers. Answer only general farming questions -- "
    "if asked something unrelated to farming, briefly say you can only help "
    "with farming and steer back. Never invent specific facts about THIS "
    "farm (its weather, its crops, its location) beyond what's given below; "
    "speak in general terms if none is given."
)

FALLBACK_TEXT = (
    "I can't look that up right now, but I can help with weather, what to "
    "plant, or a sick plant -- what would you like to know?"
)


class GeneralAgent:
    def handle(self, farm: FarmProfile, question: str | None = None) -> str:
        question = (question or "").strip()
        if not question:
            return FALLBACK_TEXT
        prompt = (
            f"Farm context (may be empty/unconfirmed -- don't assume more than this):\n"
            f"{farm.to_prompt_context()}\n\n"
            f"{farm.recent_chat_context('general')}\n\n"
            f"Farmer's question: {question}"
        )
        try:
            return llm_client.generate(prompt, system_instruction=_SYSTEM_INSTRUCTION)
        except RuntimeError:
            return FALLBACK_TEXT
