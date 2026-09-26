"""Batch-generates TTS variations of a wakeword phrase via ElevenLabs, for
use as additional positive training data alongside the real human
recordings already collected under agri_voice_agent/real_positive_raw/.

Standalone -- deliberately does NOT touch agri_voice_agent/config.py (that
module's env vars are the deployed app's runtime config; this is a one-off
local training-data tool, not something the app itself ever calls). Reads
its own ELEVENLABS_API_KEY from the environment or a .env file in the repo
root.

Usage:
    python tools/generate_wakeword_tts.py --phrase "Hey Green" --count 30

Loops over ElevenLabs' available voice library (fetched live from their
API, so it always reflects whatever voices your account actually has
access to -- the free tier includes a shared library of premade voices
across different genders/accents), generating one TTS clip per voice.
Voice-level settings (stability, similarity_boost) are randomized a little
per clip within a sane range, so even voices you cycle through more than
once (if --count exceeds the voice count) sound meaningfully different,
not identical duplicates.

Each clip is also mixed with light synthetic background noise (see
add_background_noise()) at a randomized low volume before saving -- raw
TTS output is studio-clean, and a wakeword model trained only on silent-
room audio tends to perform worse in real conditions (wind, room echo,
background chatter) than one that's seen at least SOME acoustic variation.
This is a synthetic stand-in for real ambient recordings, not a
replacement for them -- still worth supplementing with real background-
noise samples later if available.

Requested directly as raw 16kHz mono PCM from ElevenLabs (via
output_format=pcm_16000) rather than the default MP3, specifically so the
noise-mixing step below can work with plain numpy/scipy.io.wavfile --
no MP3 decode library (pydub/ffmpeg) is installed in this project, and
16kHz mono is also exactly the sample rate/channel format openWakeWord's
own classifiers are trained on, so no separate resampling step is needed
before this feeds into training either.
"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
import time
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv
from scipy.io import wavfile

load_dotenv()

API_BASE = "https://api.elevenlabs.io/v1"
REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_RATE = 16_000


def slugify(phrase: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", phrase.lower()).strip("-")


def get_api_key() -> str:
    key = os.getenv("ELEVENLABS_API_KEY", "")
    if not key:
        print(
            "ELEVENLABS_API_KEY is not set. Add it to a .env file in the repo "
            "root (ELEVENLABS_API_KEY=...) or export it in your shell.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def fetch_voices(api_key: str) -> list[dict]:
    resp = requests.get(f"{API_BASE}/voices", headers={"xi-api-key": api_key}, timeout=15)
    resp.raise_for_status()
    voices = resp.json().get("voices", [])
    if not voices:
        print("No voices returned from ElevenLabs -- check your API key/account.", file=sys.stderr)
        sys.exit(1)
    return voices


def generate_clip(api_key: str, voice_id: str, text: str) -> np.ndarray:
    """Returns int16 mono samples at SAMPLE_RATE -- raw PCM, no container/
    header, per ElevenLabs' pcm_16000 output_format."""
    # stability/similarity_boost randomized per clip (within ElevenLabs'
    # normal 0-1 range) so repeated passes over the same voice, or voices
    # reused because --count exceeds the library size, still produce
    # audibly distinct deliveries rather than identical duplicates --
    # more useful training diversity than the same clip saved twice.
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": round(random.uniform(0.3, 0.7), 2),
            "similarity_boost": round(random.uniform(0.6, 0.9), 2),
        },
    }
    resp = requests.post(
        f"{API_BASE}/text-to-speech/{voice_id}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        params={"output_format": "pcm_16000"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return np.frombuffer(resp.content, dtype=np.int16)


def add_background_noise(samples: np.ndarray) -> np.ndarray:
    """Mixes light synthetic background noise into a clean speech clip.

    Two layers, both randomized per call so the 30-clip batch doesn't all
    share one identical noise signature:
      - Pink noise (1/f spectrum) as a stand-in for generic room/ambient
        hiss -- closer to real-world background noise than pure white
        noise, which is unnaturally harsh/flat across frequencies.
      - A slow amplitude drift (very low frequency sine) layered on top,
        approximating the kind of gentle background level wander real
        ambient recordings have (wind gusts, distant traffic) rather than
        perfectly constant-level noise.

    Mixed at a randomized LOW relative volume (roughly 2-8% of the
    speech's own peak amplitude) -- enough to stop the model from only
    ever seeing dead-silent audio, not enough to mask the phrase itself
    or start looking like intentionally-corrupted data.
    """
    n = len(samples)
    # Pink noise via simple 1/f filtering of white noise in the frequency
    # domain -- adequate approximation for this purpose, no need for a
    # proper pink-noise generator library.
    white = np.random.randn(n)
    freqs = np.fft.rfftfreq(n)
    freqs[0] = freqs[1] if n > 1 else 1.0  # avoid divide-by-zero at DC
    pink_filter = 1.0 / np.sqrt(freqs)
    pink = np.fft.irfft(np.fft.rfft(white) * pink_filter, n=n)
    pink = pink / (np.abs(pink).max() + 1e-9)

    drift_freq = random.uniform(0.05, 0.3)  # very slow, a few cycles over the clip at most
    t = np.linspace(0, 1, n)
    drift = 0.5 + 0.5 * np.sin(2 * np.pi * drift_freq * t)

    noise = pink * drift
    noise_level = random.uniform(0.02, 0.08)
    speech_peak = np.abs(samples).max()
    if speech_peak == 0:
        return samples
    mixed = samples.astype(np.float64) + noise * speech_peak * noise_level
    mixed = np.clip(mixed, -32768, 32767)
    return mixed.astype(np.int16)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TTS wakeword training clips via ElevenLabs")
    parser.add_argument("--phrase", required=True, help='Wakeword phrase to synthesize, e.g. "Hey Green"')
    parser.add_argument("--count", type=int, default=30, help="Number of clips to generate (default: 30)")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: agri_voice_agent/synthetic_positive_raw/<slug>[-clean]/)",
    )
    parser.add_argument(
        "--no-noise",
        action="store_true",
        help="Skip the background-noise mixing step -- save pristine TTS output instead (default out-dir gets a '-clean' suffix so a noisy and a clean batch for the same phrase never collide)",
    )
    args = parser.parse_args()

    api_key = get_api_key()
    slug = slugify(args.phrase)
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        folder_name = f"{slug}-clean" if args.no_noise else slug
        out_dir = REPO_ROOT / "agri_voice_agent" / "synthetic_positive_raw" / folder_name
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching available voices from ElevenLabs...")
    voices = fetch_voices(api_key)
    print(f"Found {len(voices)} voices. Generating {args.count} clips for \"{args.phrase}\" into {out_dir}/")

    generated = 0
    attempt = 0
    while generated < args.count:
        voice = voices[attempt % len(voices)]
        voice_id = voice["voice_id"]
        voice_name = slugify(voice.get("name", voice_id))
        attempt += 1
        try:
            samples = generate_clip(api_key, voice_id, args.phrase)
        except requests.HTTPError as exc:
            # Free-tier character-limit exhaustion or a transient API error
            # both surface as HTTPError -- report and stop rather than
            # silently producing a short, incomplete batch.
            print(f"  [{attempt}] FAILED ({voice_name}): {exc}", file=sys.stderr)
            if exc.response is not None and exc.response.status_code in (401, 429):
                print("Stopping -- looks like a quota/auth issue, not worth retrying further.", file=sys.stderr)
                break
            continue

        if not args.no_noise:
            samples = add_background_noise(samples)
        out_path = out_dir / f"{slug}_{voice_name}_{generated:03d}.wav"
        wavfile.write(out_path, SAMPLE_RATE, samples)
        generated += 1
        print(f"  [{generated}/{args.count}] saved {out_path.name} (voice: {voice.get('name', voice_id)})")
        time.sleep(0.3)  # light pacing, avoid hammering the API

    print(f"\nDone -- {generated} clips written to {out_dir}/")
    print(
        "Next: feed this folder into openWakeWord's training pipeline alongside "
        "agri_voice_agent/real_positive_raw/ as additional positive examples."
    )


if __name__ == "__main__":
    main()
