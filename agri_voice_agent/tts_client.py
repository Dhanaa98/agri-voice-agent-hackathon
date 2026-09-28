"""Thin wrapper around ElevenLabs' text-to-speech REST API.

elevenlabs-tts branch only -- not on master. Tries to answer the "the
voice sounds robotic" ask by replacing the browser's free, zero-setup
`speechSynthesis` with a real neural voice, at the cost of a real API key,
a network round trip per reply, and ElevenLabs' free-tier character
budget (much smaller than Gemini's -- watch usage). See farmer.html's
speak()/speakAndWait() for how the frontend falls back to browser TTS if
this isn't configured or a request fails, same "degrade to the free
option, never go silent" pattern every other API integration in this
project already uses (llm_client.py, weather.py, asr.py).

Plain `requests`, not the `elevenlabs` SDK -- one small REST call doesn't
need a whole extra dependency, and every other HTTP integration in this
project (weather.py, the IP-geolocation fallback) already goes straight
through `requests` the same way.
"""

from __future__ import annotations

import requests

from . import config

BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"
REQUEST_TIMEOUT_S = 20

# eleven_multilingual_v2 -- ElevenLabs' general-purpose model, the one
# named in their own API reference as the default. Not swapped for a
# faster/cheaper "flash" model here since this branch is about voice
# QUALITY specifically ("can we make the voice not robotic") -- the
# tradeoff this branch exists to test is latency/cost for quality, so
# starting from their higher-quality default is the honest version of
# that test.
DEFAULT_MODEL = "eleven_multilingual_v2"

# mp3_44100_128 -- ElevenLabs' own documented default output_format.
# Ordinary browsers (and the <audio> element farmer.html plays this
# through) all handle MP3 natively with no extra client-side work.
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"


def synthesize_speech(text: str) -> bytes:
    """Returns MP3 audio bytes for `text`, spoken in the configured voice.

    Raises RuntimeError when no key/voice is configured, or the request
    fails for any reason -- every caller in this branch treats that as
    "fall back to browser TTS", same as llm_client.generate() raising
    RuntimeError means "fall back to the deterministic text" everywhere
    else in this project.
    """
    if not config.ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set. Copy .env.example to .env and fill it in.")
    if not config.ELEVENLABS_VOICE_ID:
        raise RuntimeError(
            "ELEVENLABS_VOICE_ID is not set. Pick a real voice_id from your ElevenLabs "
            "account's Voices list (https://elevenlabs.io/app/voice-library) and add it to .env."
        )
    if not text.strip():
        raise RuntimeError("No text to speak.")

    try:
        resp = requests.post(
            f"{BASE_URL}/{config.ELEVENLABS_VOICE_ID}",
            params={"output_format": DEFAULT_OUTPUT_FORMAT},
            headers={
                "xi-api-key": config.ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={"text": text, "model_id": DEFAULT_MODEL},
            timeout=REQUEST_TIMEOUT_S,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        # Covers HTTP error statuses (bad/expired key, invalid voice_id,
        # free-tier character quota exhausted -- ElevenLabs returns 401/
        # 422 for these) as well as transport failures (timeout, DNS,
        # connection reset). Every call site falls back to browser TTS on
        # RuntimeError, so a quota exhaustion or outage degrades safely
        # instead of surfacing a raw error or going silent.
        raise RuntimeError(f"ElevenLabs request failed: {exc}") from exc

    return resp.content
