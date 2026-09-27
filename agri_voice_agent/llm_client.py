"""Thin wrapper around the Gemini free-tier API.

Kept as a small interface so the LLM backend can be swapped (e.g. for Groq)
without touching the domain agents, per the budget constraint in the project
brief.
"""

from __future__ import annotations

import time

import httpx
from google import genai
from google.genai import errors, types

from . import config

_client: genai.Client | None = None

REQUEST_TIMEOUT_MS = 20_000

# Shared default tone across every domain agent's LLM call, so "natural"
# doesn't mean re-writing the same tone instructions in every prompt string
# (expensive to keep consistent) -- baking it into system_instruction once
# means every call site gets the same voice for free, and callers only add
# prompt text describing what to say, not how to sound. Deliberately short:
# this is speaking budget spent on TONE, not facts -- the deterministic
# assessment in each prompt is still the only source of truth for content
# (see this project's standing "LLM only phrases, never decides" rule,
# e.g. crop.py's module docstring), and gemini-flash-lite-latest was picked
# for speed, so a long system prompt would eat into that latency budget for
# no benefit.
DEFAULT_SYSTEM_INSTRUCTION = (
    "You are a warm, experienced farm advisor talking to a farmer over voice, "
    "not writing a report. Speak like you're standing in the field with them: "
    "plain words, contractions, short sentences. Never list bullet points or "
    "headers -- say it the way you'd say it out loud. Lead with the one thing "
    "that matters most to them right now, not background. Never invent facts "
    "beyond what you're given."
)


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in.")
        # No timeout by default: a stalled Gemini response (seen live) held
        # the request open indefinitely, so the assistant just went silent.
        _client = genai.Client(
            api_key=config.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
        )
    return _client


def generate(
    prompt: str,
    system_instruction: str | None = DEFAULT_SYSTEM_INSTRUCTION,
    model: str = "gemini-flash-lite-latest",
    json_mode: bool = False,
) -> str:
    """Single-turn generation. Returns plain text.

    Uses the "-latest" alias rather than a pinned version (e.g.
    "gemini-2.0-flash", which Google has since retired -- confirmed via
    client.models.list() against a live key, not assumed) so this doesn't
    silently start failing again the next time Google rotates the
    recommended fast model.

    Specifically the "flash-lite" tier, not plain "flash" -- live-timed
    against this project's key, "flash" took 23-80s per call (a farmer
    asking "what should I plant" waited over 30s, and the long-held
    connection intermittently aborted outright as a raw WinError 10053).
    "flash-lite" answered the same prompt in ~2.4s. This is a voice
    assistant; a several-second reply already stretches "conversational,"
    a 30-80s one breaks it entirely.
    """
    client = _get_client()
    config_kwargs = {"system_instruction": system_instruction} if system_instruction else {}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"
    try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )
        except errors.ServerError:
            # One quick retry for Gemini's transient 503 "high demand /
            # deadline expired" errors, seen mid-conversation in testing --
            # usually gone a second later. Client errors (4xx) aren't retried.
            time.sleep(1.5)
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )
    except errors.APIError as exc:
        # Covers both server-side outages (e.g. a transient 503 "model
        # experiencing high demand") and client-side failures (bad model
        # name, quota exceeded, auth problems). Every call site already
        # falls back to deterministic text on RuntimeError (the "no key
        # configured" case) -- re-raising as RuntimeError here means a
        # temporary Gemini outage degrades to that same safe fallback
        # instead of surfacing a raw API error/stack trace to the farmer.
        raise RuntimeError(f"Gemini request failed: {exc}") from exc
    except (OSError, httpx.HTTPError) as exc:
        # Transport-level failures (connection aborted/reset, DNS hiccup,
        # timeout) surface as raw OSError/ConnectionError from the
        # underlying HTTP client, not errors.APIError -- observed live as
        # "[WinError 10053] An established connection was aborted by the
        # software in your host machine" leaking straight into a farmer's
        # chat bubble. Same fallback treatment as an API-level failure.
        raise RuntimeError(f"Gemini request failed: {exc}") from exc
    return response.text.strip()
