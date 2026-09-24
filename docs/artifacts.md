# Published Artifacts

Two published artifacts exist for this project, both under this
account and both meant to be updated in place (same `url`) rather than
republished as new pages when the underlying project data/architecture changes.

- **Pathogen Ledger** — https://claude.ai/artifact/Vco1gE3bRop8jdGKCS7ELS
  Browsable UI over the live `plant_data.py` disease dataset: crop rail +
  disease cards + global search across name/pathogen/symptom text,
  region-tagged control entries visually distinguished from universal ones,
  weather-trigger thresholds shown per disease. Data is exported from
  `plant_data.py` via a one-off Python script and embedded inline as JSON in
  the page (not fetched live), so it goes stale if `plant_data.py` changes
  without a republish.
  **Republish steps:** regenerate `scratchpad/pathogen_data.json`, do a
  targeted string-replace of the `const DATA = ...;` blob in
  `scratchpad/pathogen_browser.html`, verify crop/disease counts parse
  correctly before publishing, then Artifact-publish with the same `url`
  (not a fresh `file_path`) to update in place.

- **Agri Voice Agent Layout** — https://claude.ai/artifact/2KDxhdNsyR6hRUZgCb1gPE
  Architecture diagram + file-tree map of the project. Now stale on FOUR
  points as of 2026-09-21 (plus a further phrase change on 2026-09-23) and
  needs regenerating before it's shown to anyone: (1) it still shows three
  wakewords ("Hey Weather"/"Hey Crop"/"Hey Plant") — the real system is now
  two ("Hey Green" covering both Weather and Crop via `intent.py`'s
  `resolve_field_domain()`, plus "Hey Doc" for plant diagnosis, renamed
  from "Hey Plant" on 2026-09-21 -- internally still the "plant"
  domain/filename, only the spoken phrase changed; the Weather+Crop phrase
  itself later changed again, "Hey Field" -> "Hey Green" on 2026-09-23,
  internally still the "field" domain/filename); (2) it doesn't reflect that the farmer-facing dashboard routes
  via a single `/chat` endpoint with `intent.py` picking the agent, not
  three separate buttons/endpoints; (3) `FarmState` is now a list of
  `FarmProfile` entries (multi-farm support) rather than one flat object;
  (4) doesn't reflect the real browser-side openWakeWord 3-stage detection
  pipeline (melspectrogram -> embedding -> classifier, all client-side via
  onnxruntime-web) now backing both wakewords in the farmer dashboard.
  Regenerate and republish to the same `url` next time this project's
  architecture is touched or explained to someone else.

**Why this matters:** both pages are embedded snapshots, not live views —
neither auto-updates when the underlying code changes. Check this memory
before claiming either artifact reflects "current" state, and republish to
the existing `url` (never a new one) so the link stays stable for anyone
who already has it open or bookmarked.
