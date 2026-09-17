"""Thin wrapper around the Gemini free-tier API.

Kept as a small interface so the LLM backend can be swapped (e.g. for Groq)
without touching the domain agents, per the budget constraint in the project
brief.
"""

from __future__ import annotations

from google import genai
from google.genai import errors, types

from . import config

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in.")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def generate(prompt: str, system_instruction: str | None = None, model: str = "gemini-flash-lite-latest") -> str:
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
    try:
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
    except OSError as exc:
        # Transport-level failures (connection aborted/reset, DNS hiccup,
        # timeout) surface as raw OSError/ConnectionError from the
        # underlying HTTP client, not errors.APIError -- observed live as
        # "[WinError 10053] An established connection was aborted by the
        # software in your host machine" leaking straight into a farmer's
        # chat bubble. Same fallback treatment as an API-level failure.
        raise RuntimeError(f"Gemini request failed: {exc}") from exc
    return response.text.strip()
