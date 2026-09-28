# Architecture

Current, accurate description of the system as it actually runs today. The
top-level `README.md` describes the original hackathon build plan and is
stale in places (predates per-farmer identity, the context interpreter, and
the deployment); this document supersedes it for anything about how the
farmer-facing app (`farmer_server.py` + `static/farmer.html`) currently
works. `docs/build_log.md` has the full chronological history of every fix
and decision — this document is the settled, "what it does now" summary.

## What this is

A voice/chat farm assistant. A farmer manages one or more farms, asks
questions about weather, what to plant, and sick plants, and gets answers
grounded in real weather data, a fixed crop-suitability dataset, and a
disease reference — not free-form LLM guessing about facts. There are two
front ends:

- **`farmer_server.py` + `static/farmer.html`** — the real product. A single
  FastAPI server, one page, typed chat + voice input, multi-farm support,
  deployed to Render. Everything below describes this one.
- **`dashboard_server.py` + `static/index.html`** and **`main.py`** — an
  earlier technical/demo view over a continuous wakeword-listening loop
  (`main.py`'s `VoiceAgentLoop`), useful for showing the cross-domain
  reasoning live but not the farmer-facing product.

## Request flow

Every message — typed or spoken — ends up at `_answer()` in
`farmer_server.py`. In order:

1. **Farm-state resolution** (`_use_farm_state(farmer_id)`) — binds the
   request to that farmer's own `FarmState`, never a shared global one.
2. **Farewell check** — "thanks", "bye", etc. end the conversation cleanly.
3. **Mic-check check** — "can you hear me" gets a direct answer, not routed
   anywhere.
4. **Pending-new-farm-location** — if the farmer was just asked "what town
   is it in?" after adding a farm, the reply is applied directly.
5. **Farm management** (`_handle_farm_management`) — add / delete / rename /
   relocate / list a farm, and a bare farm name ("Farm 1") on its own.
   **Regex-only, never LLM-routed** — see "Why farm commands stay regex"
   below.
6. **Pending farm-choice** — if the farmer has 2+ farms and hasn't said
   which one a conversation is about yet.
7. **Pending location question** — weather/crop questions that needed a
   location and are now getting one.
8. **Keyword domain routing** (`intent.py`'s `detect_domain()`) — fast,
   deterministic, word-boundary matched.
9. **Context interpreter** (`interpreter.py`) — only when nothing above
   matched. One Gemini call, JSON-mode, sees the farm list, the farm in
   focus, and the last 10 conversation turns, and returns a structured
   action: route to a domain (question rewritten to stand alone), select a
   farm, add a farm, answer directly, or ask a specific clarifying
   question.
10. **Domain agent call** — `WeatherAgent` / `CropAgent` / `PlantAgent`
    handle the actual question against the farm's saved state.

## The three domains + the interpreter

| Domain | Deterministic core | LLM's job |
|---|---|---|
| **Weather** (`domains/weather.py`) | Live OpenWeatherMap current + 7-day forecast, real geocoding | Phrase the forecast conversationally |
| **Crop** (`domains/crop.py`) | Fixed `crop_data.py` dataset (45 crops), scored against the farm's real climate/location, disease history folded in as warnings | Phrase the verdict; for a "how do I grow X" question, generate general growing steps (assessment passed as background, not the answer) |
| **Plant** (`domains/plant.py`) | Multi-turn symptom-collection state machine, then matched against `plant_data.py`'s disease reference (43 crops / 223+ diseases, weather-trigger-aware, region-aware control advice) | Phrase the final diagnosis and ask the follow-up questions |
| **Interpreter** (`interpreter.py`) | None — this is the one deliberate exception | The whole answer, for anything the above three don't cover (open-ended farming questions, context-dependent follow-ups, farm selection by description) |

In every domain except the interpreter, **the LLM never decides a fact** —
it only turns already-computed data into natural spoken language. If
`GEMINI_API_KEY` isn't set, every domain falls back to the plain
deterministic text instead of crashing.

## Why farm commands stay regex

Deleting, renaming, relocating, or adding a farm is destructive/persistent
enough that a wrong LLM guess would be worse than just not recognizing the
command. These are matched by fixed regex patterns
(`_ADD_FARM_RE`, `_DELETE_FARM_RE`, etc.) and a confirmation step before
delete ("Delete Farm 2? This can't be undone — say yes to confirm"). The
context interpreter can *also* trigger `select_farm`/`add_farm` for
naturally-phrased requests it recognizes, but delete/rename/relocate are
**never** reachable through it — only through the exact regex commands.

## Per-farmer data isolation

Every farmer's farms are scoped by a `farmer_id` — a UUID the browser
generates once and stores in `localStorage`, sent with every request. This
replaced an earlier design where all farm data was one shared global list
(a real bug: a second person's test farm was visible from a different
phone). Pre-multi-farmer data migrates once to whichever real `farmer_id`
asks first after deploy.

`session_id` is a **separate**, per-browser-tab identifier (not persisted,
regenerated on every page load) that scopes which farm a given
*conversation* is currently about, and short-lived state like a pending
location question — distinct from `farmer_id`, which scopes which farms
*exist* at all.

## Voice input: two different paths

- **Push-to-talk (mic button)** — uses the browser's own built-in
  `SpeechRecognition` API. No server round-trip, no API key, text appears
  live in the input box as you speak, Enter/Send works exactly like typing.
  Not supported in Firefox (button stays hidden there).
- **Always-listening wakeword mode** ("Hey Green", opt-in toggle) —
  wakeword *detection* runs entirely client-side (`onnxruntime-web`, no
  audio leaves the device until the wakeword fires). Once triggered, the
  actual question is streamed server-side to **AssemblyAI** (`asr.py`,
  `universal_streaming_english` model) over a WebSocket, then routed to
  weather/crop/plant via the same keyword+interpreter logic described
  above — the wakeword only decides *when* to start listening, never
  which domain answers. One wakeword covers all three domains as of
  2026-09-28 (previously two: "Hey Green" for weather/crop, "Hey Doc"
  kept separate for plant diagnosis — consolidated to one, explicit user
  choice). This is the one voice path that needs `ASSEMBLYAI_API_KEY`
  configured and has not been exercised against a real microphone in this
  dev environment — verify live before relying on it for a demo.

Spoken replies (both paths) use the browser's built-in `speechSynthesis` —
no server-side TTS exists anywhere in this project.

## Latency budget

See `docs/USER_GUIDE.md`'s "What to expect" section for the farmer-facing
version of this. Concrete sources, for anyone modifying the code:

- Gemini (`gemini-flash-lite-latest`) — ~2-3s typical for a single call.
  Every LLM-backed reply (weather phrasing, crop verdicts, plant diagnosis,
  the interpreter fallback) costs one call. A hard 20s timeout
  (`llm_client.REQUEST_TIMEOUT_MS`) degrades to fallback text instead of
  hanging.
- Keyword-matched messages (weekday phrasing hits `detect_domain()`) skip
  the interpreter entirely — no extra LLM call, same ~2-3s domain-agent
  cost as any other reply.
- Interpreter-routed messages (no keyword match) cost one extra Gemini
  call before the domain agent's own call — roughly double the latency of
  a keyword-matched message.
- OpenWeatherMap calls — 10s timeout per request (`domains/weather.py`),
  typically much faster live.
- AssemblyAI WebSocket handshake — observed ~4.6-4.8s before the socket is
  actually ready to receive audio (an SDK-internal retry after an initial
  SSL handshake timeout); the frontend waits for an explicit "ready"
  message before starting mic capture, masked by a spoken greeting so it
  doesn't feel like dead air.
- `/resolve_location`'s IP-geolocation fallback — 5s timeout against
  ip-api.com's free tier.

## Known gaps / not yet verified

- The AssemblyAI wakeword-voice path (see above) — needs a live device
  test with a real key.
- No request locking on `SessionState` — concurrent requests on the same
  session (e.g. a double-tap send) aren't synchronized. Not expected to
  bite in normal single-farmer usage.
- `_sessions` (per-tab state) has no eviction — grows for the life of the
  server process. Not a concern for a demo-length session.

## Project layout

See `README.md`'s "Project layout" section — file locations haven't
changed, only what's described above about how they're wired together.
