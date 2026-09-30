# Agricultural Voice Agent

Multi-wakeword voice agent for farmers, built for the AssemblyAI Voice Agent
Hackathon (lablab.ai). Full design in [AGRI_VOICE_AGENT_BRIEF.md](AGRI_VOICE_AGENT_BRIEF.md).

**For how the app actually works today** (per-farmer accounts, the context
interpreter, current voice input paths, latency expectations), see
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/USER_GUIDE.md](docs/USER_GUIDE.md) — sections of this README below
(deployment status, push-to-talk needing AssemblyAI) describe the original
build plan and are out of date. [docs/build_log.md](docs/build_log.md) has
the full chronological history of every fix.

Two wakewords route to three domain agents that share one `FarmState` object:

- **"Hey Green"** — covers both Weather (live conditions + forecast, OpenWeatherMap
  free tier) and Crop (suitability advice, rule-based, informed by weather + disease
  history). Which one answers is resolved from the transcript after the wakeword
  fires (`intent.py`'s `resolve_field_domain()`, deterministic keyword matching, same
  mechanism the farmer dashboard's chat uses) — these two were originally separate
  wakewords ("Hey Weather"/"Hey Crop") but were merged since both are short, single-
  shot informational questions a farmer asks without first deciding which specialist
  they want, and "Hey Crop" alone was acoustically weak (short, hard-stop ending, too
  close to "Hey Plant", the original phrase for the domain below).
- **"Hey Doc"** — voice-only disease diagnosis via targeted follow-up questions.
  Kept as its own wakeword since it's a different conversation shape (multi-turn,
  symptom-driven) rather than a one-shot question. Originally "Hey Plant", renamed
  for a friendlier "plant doctor" framing (internally still the "plant" domain).

## Live demo

**Not yet deployed.** The farmer dashboard (`farmer_server.py`) is deployment-ready
for [Render](https://render.com)'s free tier — `render.yaml`, `Procfile`, and a slim
`requirements-deploy.txt` are already in place, and the server reads `$PORT`/binds
`0.0.0.0` when running under a cloud host. A git repo exists locally with an initial
commit but hasn't been pushed to GitHub yet. To deploy:

1. `gh repo create agri-voice-agent --public --source=. --remote=origin --push`
   (or push to a GitHub repo you create manually)
2. On [render.com](https://render.com): New → Web Service → connect the repo →
   it should auto-detect `render.yaml`
3. Add `GEMINI_API_KEY`, `OPENWEATHER_API_KEY`, and (optionally) `ASSEMBLYAI_API_KEY`
   as environment variables in Render's dashboard
4. Deploy — you'll get a public URL that works on any device, including mobile

Until that's done, run it locally (see below) and access it at `http://localhost:8001`.

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill in `.env`:
- `ASSEMBLYAI_API_KEY` — for streaming ASR
- `GEMINI_API_KEY` — Google AI Studio free tier
- `OPENWEATHER_API_KEY` — OpenWeatherMap free tier

## Status

- [x] Project scaffold: shared `FarmState`, Gemini LLM client, wakeword router stub
- [x] Weather domain agent (end-to-end, live API)
- [x] Crop-suitability domain agent (rule-based, cross-domain tested)
- [x] AssemblyAI streaming ASR integration (`asr.py`)
- [x] Microphone audio capture (`audio_input.py`)
- [x] Main orchestration loop wiring wakeword → ASR → domain agent → shared state (`main.py`)
- [x] Plant-disease diagnostic conversation (primary focus) — multi-turn follow-up
      questions, deterministic weather-weighted cause ranking. Named-disease
      coverage spans **43 crops / 163 diseases** in `plant_data.py`, built in two
      distinct layers:
      - The original **5 core crops** (tomato, chili, rice, okra, onion — the
        crops `crop_data.py` also has growing-condition data for) hold 23
        hand-picked, best-documented entries across five sourcing passes: a 1943
        public-domain Montana bulletin, a general plant pathology textbook,
        regional Indian crop-disease guides (TNAU, AGS322), and — web-sourced,
        not user-supplied — NMSU Circular 549 "Chile Pepper Diseases" and the
        Texas A&M Plant Disease Handbook.
      - **38 more crops** (soybean, wheat, potato, mango, and many others) hold
        140 comprehensively-promoted entries converted from
        `plant_pathology_reference.md`'s full catalog — every disease with real
        symptom+control detail, not hand-picked curation. A few crops (e.g.
        cabbage/cauliflower, cucumber/melon, coconut) resolve through
        `_CROP_ALIASES` to a shared multi-host group entry (crucifers,
        cucurbits, palms) since the source documents them as one disease set.
      Named diseases with sourced weather data (e.g. rice Blast/Brown spot/Sheath
      blight, chili anthracnose/Phytophthora blight) carry a structured
      `WeatherTrigger` (real temperature/humidity thresholds or a qualitative
      condition from the source, never a guess) and the diagnosis states whether
      current conditions match — diseases with no sourced trigger get no weather
      commentary at all rather than an invented one. Also does a deterministic
      biotic-vs-abiotic sanity check (sourced from a Univ. of Nebraska Extension
      symptom-terminology bulletin) — if the farmer's wording suggests a
      nonliving cause (unrelated plants affected, no spread, a sharp margin, a
      named chemical/sprinkler issue), the diagnosis surfaces a caveat instead of
      confidently blaming a pathogen. See `domains/plant.py` and
      `domains/plant_data.py`. Full reference (~223+ diseases across 43 crops —
      plant_data.py's comprehensive-promotion crops now match it 1:1, aside from
      banana, which the source doc itself flagged as too thin to convert) in
      `plant_pathology_reference.md`.
      Control advice is also **region-aware**: each disease's `control` is a list
      of `RegionalControl` entries — universal agronomic practice always shows,
      while a region-specific entry (a named fungicide product, a variety bred
      for one place, e.g. TNAU/Tamil Nadu doses) only shows when `farm_state`'s
      `country_code` (set from the Weather agent's geocoding lookup) actually
      matches. Unknown or non-matching regions get only the universal advice —
      no region is ever treated as a default, including the regions most of the
      current source material happens to come from. See `get_control_for_region()`
      in `plant.py`.
- [x] Crop-suitability advisor also expanded — `crop_data.py` grew from 5 to
      **45 `CropProfile` entries** (40 new, hand/research-sourced growing-condition
      data: ideal temperature/humidity ranges and max weekly rainfall, checked
      against real agronomic sources per crop, not invented). Same deterministic
      scoring as the original 5 — the LLM only phrases the output, never decides
      suitability.
- [x] Live demo dashboard (frontend) — local FastAPI + WebSocket server
      (`dashboard_server.py`) broadcasting live state/transcript/response/farm_state
      events to a single-page HTML dashboard (`static/index.html`) showing the
      active domain, conversation feed, and shared farm_state (weather, crops,
      symptom history) updating in real time. Runs the existing `VoiceAgentLoop`
      unmodified in a background thread.
- [x] Cross-domain integration pass — `tests/test_cross_domain_integration.py`
      chains Weather → Plant → Crop against one shared `FarmState` and asserts
      (not just prints) that the chain actually changes output at each step:
      the same symptom under humid vs. dry weather produces a different Plant
      diagnosis, and Crop's advice is asserted to reference that diagnosis in
      its warnings. This is the concrete proof of the "one integrated agent,
      not three features" claim. Supports `--live` to pull real weather once
      `OPENWEATHER_API_KEY` is set.
- [ ] Wakeword models (.onnx) — to be dropped into `agri_voice_agent/wakeword/models/`
      as `field.onnx`, `plant.onnx` (two models now, not three — see "Hey Green" above)
- [ ] Live end-to-end test with real API keys + mic (only import/wiring verified so far)

## Try it now

```
python -m agri_voice_agent.tests.test_weather_manual
python -m agri_voice_agent.tests.test_crop_manual
python -m agri_voice_agent.tests.test_plant_manual
python -m agri_voice_agent.tests.test_cross_domain_integration
```

The Plant test demonstrates the cross-domain claim directly: the same symptom
("the leaves are wilting") on the same crop produces a different top-ranked
cause depending on whether `farm_state`'s current weather is humid/wet or dry.
The cross-domain integration test goes one step further and asserts the full
chain: Weather shifts the Plant diagnosis, and Crop's advice is checked to
actually reference that diagnosis — proving Plant's output reaches Crop, not
just sitting unused in `farm_state`.

Once `.env` has `ASSEMBLYAI_API_KEY` set, you can also test the full mic → ASR →
domain-agent path without wakeword models yet:

```
python -m agri_voice_agent.main --domain crop
```

This skips wakeword detection and goes straight into the Crop domain — say
something and it'll transcribe, run the crop assessment, and print a response.

## Live dashboard (technical / demo view)

```
python -m agri_voice_agent.dashboard_server --domain crop
```

Then open http://localhost:8000 in a browser. Runs the full voice agent loop
in the background and streams live updates to the page — the active domain,
the conversation transcript/responses, and the shared farm_state panel (so
you can visually show weather or a Plant diagnosis changing what Crop says
next). Omit `--domain` once wakeword `.onnx` models are in place to let both
wakewords ("Hey Green", "Hey Doc") route naturally instead of forcing one
domain. Built to prove
the cross-domain reasoning claim during a demo — not meant for a farmer to
actually use day to day (raw state, debug-style transcript log).

## Farmer dashboard (click-to-activate)

```
python -m agri_voice_agent.farmer_server
```

Then open http://localhost:8001. A second, plain-language front end: three
large buttons (Weather / Crop / Plant Health) the farmer taps instead of
speaking a wakeword, then types (or speaks, once a microphone path is wired
up — see below) their question directly to that agent. No wakeword models or
continuous mic stream needed — the click *is* the activation. Shares the same
`FarmState` file as the technical dashboard, so a diagnosis logged here shows
up there too.

- **Typed input** — fully built and tested end-to-end (`POST /chat`, single
  endpoint that auto-routes to the right domain via `intent.py`). Works today
  with zero extra setup beyond what's already optional (`GEMINI_API_KEY`
  improves phrasing; without it, responses show as the plain structured text,
  same fallback the rest of the project uses).
- **Voice input** — this is a farmer-facing voice agent, so the dashboard has
  a real browser voice pipeline, not just typed chat:
  - **Push-to-talk** — the mic button appears once `ASSEMBLYAI_API_KEY` is
    set; tap, speak, tap again (or it auto-stops), transcribed via
    `WS /voice` the same way `main.py`'s local pipeline transcribes speech.
  - **Always-listening wakeword mode** — an opt-in toggle (continuous mic
    access is never on by default) that runs your `.onnx` wakeword model(s)
    **client-side** in the browser via `onnxruntime-web`, scoring audio
    frames locally with no audio leaving the device until the wakeword
    actually fires. Appears only once a `.onnx` file is actually present
    under `agri_voice_agent/wakeword/models/` (served to the browser via a
    `/wakeword-models/` static mount) — same fail-gracefully pattern as the
    rest of this project.
  - **Spoken replies** — voice-triggered answers are also read aloud via the
    browser's built-in `speechSynthesis` (Web Speech API) — free, no new API
    key, keeps the project's free-tier-only constraint.
  - **Not yet tested against a real microphone, browser, or trained model**
    — no `.onnx` wakeword files exist yet (same standing blocker as the
    local pipeline), and no `ASSEMBLYAI_API_KEY` is configured in this dev
    environment. The wakeword scoring function's model input/output
    contract is also explicitly a placeholder (see `docs/build_log.md`) —
    it assumes a single end-to-end `.onnx` model, which does NOT match
    openWakeWord's real 3-stage architecture; verify/adjust once a real
    trained model exists.
- `GET /capabilities` tells the page what's actually usable (mic, wakeword
  models, phrasing) so it never offers a control that would just fail.
- **Location** — a blocking modal asks for the farm's location the first
  time a weather-routed question comes up with none known yet (GPS
  auto-detect, IP-based fallback, or manual entry — never asked again once
  confirmed, remembered via `localStorage` across visits). Live-verified
  with a real query (London, GB returned real London conditions).

## Project layout

```
plant_pathology_reference.md  # full disease catalog, organized by crop (see its own Index/Sources tables)

docs/
  build_log.md         # running step-by-step build progress log
  project_overview.md    # top-level project summary

agri_voice_agent/
  farm_state.py       # shared cross-domain state
  intent.py             # deterministic keyword routing -- "Hey Green" -> weather/crop, farmer dashboard chat
  llm_client.py        # Gemini free-tier wrapper
  config.py             # env/config loading
  asr.py                 # AssemblyAI streaming ASR wrapper
  audio_input.py          # microphone capture, shared by wakeword + ASR
  main.py                  # orchestration loop: wakeword -> ASR -> domain -> response
  events.py                # AgentEvent/EventBus -- decouples main.py from any UI
  dashboard_server.py       # FastAPI + WebSocket server hosting the technical dashboard
  farmer_server.py           # FastAPI server for the farmer-facing click-to-activate dashboard
  static/
    index.html            # technical dashboard (conversation log + raw farm_state)
    farmer.html             # farmer dashboard (tap-to-activate, plain language)
  wakeword/
    router.py           # multi-model ONNX wakeword routing (models dropped in by user)
  domains/
    weather.py           # "Hey Green" -> weather (resolved via intent.py after wakeword)
    crop.py               # "Hey Green" -> crop (resolved via intent.py after wakeword)
    crop_data.py           # fixed crop suitability lookup table
    plant.py               # "Hey Doc" -- multi-turn diagnostic conversation
    plant_data.py           # symptom/cause framework + named tomato/onion diseases
  tests/
    test_weather_manual.py
    test_crop_manual.py
    test_plant_manual.py
    test_cross_domain_integration.py  # Weather -> Plant -> Crop chained, asserts real cross-domain shift
```
