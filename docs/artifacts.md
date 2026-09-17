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
  Architecture diagram + file-tree map of the project. Now stale on THREE
  points as of 2026-09-17 and needs regenerating before it's shown to
  anyone: (1) it still shows three wakewords ("Hey Weather"/"Hey Crop"/
  "Hey Plant") — the real system is now two ("Hey Field" covering both
  Weather and Crop via `intent.py`'s `resolve_field_domain()`, plus "Hey
  Plant"); (2) it doesn't reflect that the farmer-facing dashboard routes
  via a single `/chat` endpoint with `intent.py` picking the agent, not
  three separate buttons/endpoints; (3) `FarmState` is now a list of
  `FarmProfile` entries (multi-farm support) rather than one flat object.
  Regenerate and republish to the same `url` next time this project's
  architecture is touched or explained to someone else.

**Why this matters:** both pages are embedded snapshots, not live views —
neither auto-updates when the underlying code changes. Check this memory
before claiming either artifact reflects "current" state, and republish to
the existing `url` (never a new one) so the link stays stable for anyone
who already has it open or bookmarked.
