# HeyGreen

A voice-first farm assistant for the AssemblyAI Voice Agent Hackathon
(lablab.ai). Full original design in
[AGRI_VOICE_AGENT_BRIEF.md](AGRI_VOICE_AGENT_BRIEF.md);
[docs/build_log.md](docs/build_log.md) has the full chronological history
of every fix and feature since.

Say **"Hey Green"** and ask about the weather, what to plant, or a sick
plant. One wakeword opens a conversation with three domain agents that
share a single `FarmState` object, so a wet forecast can change a plant
diagnosis, and that diagnosis can change crop advice in the same
conversation.

- **Weather** — live conditions and a 7-day forecast (OpenWeatherMap free
  tier).
- **Crop planning** — suitability scoring across 51 crops, weighed against
  the farm's real forecast and any recent plant diagnosis.
- **Plant health** — voice-only diagnosis (no photo needed) across a
  knowledge base of 198 named diseases, reached through a few targeted
  follow-up questions rather than a single guess.

Which domain answers a "Hey Green" question is resolved deterministically
from the transcript (`intent.py`'s keyword routing) — the LLM never
decides that either.

## Live demo

Deployed on Render's free tier: **https://agri-voice-agent-farmer.onrender.com**

The free tier spins down when idle, so the first load after a while can
take up to a minute to wake up — wait rather than refresh.

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill in `.env`:
- `ASSEMBLYAI_API_KEY` — streaming ASR (required for any voice input path)
- `GEMINI_API_KEY` — Google AI Studio free tier (phrasing only; the app
  still answers correctly without it, just in plainer language)
- `OPENWEATHER_API_KEY` — OpenWeatherMap free tier
- `OPENAI_API_KEY` — optional paid fallback, only ever called if a Gemini
  request itself fails (outage/quota). Leave unset to stay 100% free-tier.
- `ELEVENLABS_API_KEY` / `ELEVENLABS_VOICE_ID` — optional cloud
  text-to-speech for spoken replies; without these the app falls back to
  the browser's own free `speechSynthesis`.

Run the farmer dashboard:

```
python -m agri_voice_agent.farmer_server
```

Then open `http://localhost:8001`.

## How voice input works

- **Hold-to-talk mic button** — press and hold, speak, release. On
  desktop/Android release just stops listening (Enter/Send sends);
  on touch, releasing sends immediately unless you slide sideways to
  cancel first, the same gesture as a WhatsApp voice message. Desktop and
  Android use the browser's own `SpeechRecognition`; iOS routes through
  the same AssemblyAI streaming pipeline the wakeword flow uses, since
  `SpeechRecognition` is unreliable across every iOS browser (they're all
  WebKit under the hood).
- **Always-listening wakeword mode** — opt-in (never on by default),
  detects "Hey Green" fully client-side via a custom openWakeWord model
  running in the browser through `onnxruntime-web`. No audio leaves the
  device before the wakeword actually fires.
- **Manual trigger button** — a standing "Enable HeyGreen" button in the
  panel header does exactly what a real on-device detection does
  (greeting, then a multi-turn conversation), useful when you want to
  start a voice exchange without relying on the wakeword actually being
  heard.
- **Spoken replies** — read aloud via ElevenLabs (if configured) or the
  browser's free `speechSynthesis` otherwise.

`GET /capabilities` tells the page what's actually usable (mic, wakeword
models, cloud TTS) so it never offers a control that would just fail.

## Testing the domain agents directly

```
python -m agri_voice_agent.tests.test_weather_manual
python -m agri_voice_agent.tests.test_crop_manual
python -m agri_voice_agent.tests.test_plant_manual
python -m agri_voice_agent.tests.test_cross_domain_integration
```

The cross-domain integration test is the concrete proof of the "one
integrated agent, not three features" claim: it chains Weather → Plant →
Crop against one shared `FarmState` and asserts that the same symptom
produces a different Plant diagnosis under humid vs. dry weather, and
that Crop's advice actually references that diagnosis.

## Project layout

```
AGRI_VOICE_AGENT_BRIEF.md       # original hackathon design brief
plant_pathology_reference.md    # full disease catalog, organized by crop

docs/
  build_log.md                  # running step-by-step build progress log
  project_overview.md           # top-level project summary

submission/                     # lablab.ai submission text + cover image

agri_voice_agent/
  farm_state.py                 # shared cross-domain state, persisted per farmer
  intent.py                     # deterministic keyword routing after "Hey Green"
  llm_client.py                 # Gemini wrapper, with an optional OpenAI fallback
  tts_client.py                 # ElevenLabs cloud TTS wrapper (optional)
  config.py                     # env/config loading
  asr.py                        # AssemblyAI streaming ASR wrapper
  farmer_server.py              # FastAPI server for the deployed farmer dashboard
  static/
    farmer.html                 # the real, deployed farmer-facing app
    index.html, wakeword_test.html  # earlier technical/debug dashboards
  wakeword/
    router.py                   # multi-model ONNX wakeword routing (local pipeline)
    models/                     # .onnx wakeword model files
  domains/
    weather.py                  # live conditions + forecast
    crop.py                     # crop suitability scoring
    crop_data.py                # crop growing-condition lookup table
    plant.py                    # multi-turn diagnostic conversation
    plant_data.py               # symptom framework + named-disease knowledge base
  tests/
    test_weather_manual.py
    test_crop_manual.py
    test_plant_manual.py
    test_cross_domain_integration.py
```
