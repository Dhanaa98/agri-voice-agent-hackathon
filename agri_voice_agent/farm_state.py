"""Shared farm-state object read and written by all three domain agents.

Plain structured data, no LLM involved in maintaining it. This is the
mechanism that makes cross-domain reasoning real: each domain agent reads
context written by the others before it responds.

A farmer can have more than one farm (different fields, different regions),
so the state is a list of named FarmProfile entries plus which one is
currently "active" -- the domain agents themselves only ever see a single
FarmProfile (whichever one is active), same as before this was introduced;
only the server layer (farmer_server.py) deals with the list/selection.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class SymptomReport:
    crop: str
    symptoms: str
    date: str
    diagnosis: str | None = None


@dataclass
class ChatTurn:
    """One side of one exchange -- a farmer's message or an agent's reply.
    Persisted as a flat, growing list per farm (see FarmProfile.chat_history),
    not scoped to any one session -- recent_chat_context() below is what
    turns this into "memory": it doesn't matter whether the last few turns
    for a domain happened a minute ago or a week ago, they're recalled the
    same way either time."""

    domain: str
    role: str  # "farmer" | "agent"
    text: str
    timestamp: str


@dataclass
class TranscriptEntry:
    """One visible chat bubble, farmer-scoped (not per-farm, not per-tab) --
    what makes the on-screen conversation survive a page refresh. Distinct
    from FarmProfile.chat_history (ChatTurn above): that only records a
    turn when a specific farm is already attached, so farm-management
    replies ("add a farm", "what farms do I have", a farewell) never
    appeared in it. This records every reply the farmer actually saw,
    farm-attached or not, in the same "kind" vocabulary the frontend's
    addMessage() already uses, so the page can just replay these on load
    instead of the chat log starting empty every time -- see GET
    /conversation in farmer_server.py."""

    kind: str  # "you" | "agent" | "notice"
    domain: str | None
    text: str
    timestamp: str


@dataclass
class WeatherSnapshot:
    temp_c: float | None = None
    humidity_pct: float | None = None
    rainfall_recent_mm: float | None = None
    rainfall_forecast_7day_mm: float | None = None
    condition: str | None = None
    fetched_at: str | None = None


@dataclass
class FarmProfile:
    """One farm's worth of state -- what used to be the whole of FarmState
    before a farmer could have more than one farm. Everything domain agents
    (WeatherAgent, CropAgent, PlantAgent) read/write is scoped to whichever
    FarmProfile is currently active; they never see the farm list itself."""

    name: str = "Farm 1"
    location: str = ""
    # ISO 3166-1 alpha-2 country code (e.g. "IN", "US", "AU"), set from the
    # Weather agent's geocoding lookup when available. Empty string means
    # unknown -- domain agents that filter advice by region (see plant.py's
    # get_control_for_region) treat unknown the same as "show only the
    # universal/general entries", never assuming any one country.
    country_code: str = ""
    # True only once a farmer has actually supplied a location (typed into
    # the location box, or spoken). WeatherAgent.handle() still falls back
    # to config.DEFAULT_LOCATION when this is False so a demo works with
    # zero setup, but that fallback must never look "known" afterwards --
    # otherwise the location prompt stops appearing after the very first
    # query, which is exactly what happened before this flag existed: the
    # default silently got written into `location` and every later call
    # then saw a non-empty `location` and assumed it was farmer-given.
    location_confirmed: bool = False
    current_weather: WeatherSnapshot = field(default_factory=WeatherSnapshot)
    crops_grown: list[str] = field(default_factory=list)
    recent_symptoms_reported: list[SymptomReport] = field(default_factory=list)
    regional_disease_notes: list[str] = field(default_factory=list)
    # Full raw transcript, per farm, across every session -- see ChatTurn's
    # docstring. Capped on append (see add_chat_turn) so a long-lived farm
    # profile can't grow this file without bound.
    chat_history: list[ChatTurn] = field(default_factory=list)

    def add_crops_grown(self, crops: list[str]) -> None:
        """Record crops the farmer has said they're actually growing on
        this farm -- see domains/crop.py's mentioned_crops_grown() for how
        a message is recognised as this kind of statement rather than a
        suitability/how-to question. Deduplicated case-insensitively (crop
        names are stored/matched lowercase elsewhere, e.g. CropAgent.
        assess_one()) so "I grow rice" then later "I'm also growing Rice"
        doesn't double up."""
        existing = {c.lower() for c in self.crops_grown}
        for crop in crops:
            if crop.lower() not in existing:
                self.crops_grown.append(crop)
                existing.add(crop.lower())

    def add_symptom_report(self, crop: str, symptoms: str, diagnosis: str | None = None) -> None:
        self.recent_symptoms_reported.append(
            SymptomReport(
                crop=crop,
                symptoms=symptoms,
                date=datetime.now(timezone.utc).isoformat(),
                diagnosis=diagnosis,
            )
        )

    # Cap on chat_history length -- generous for a hackathon/demo lifetime
    # (roughly 100 exchanges per farm) while keeping the on-disk FarmState
    # JSON from growing unbounded. Full raw transcript was an explicit
    # choice over summarization, so trimming the oldest turns (rather than
    # compacting them) is the only growth control here.
    MAX_CHAT_HISTORY = 200

    def add_chat_turn(self, domain: str, role: str, text: str) -> None:
        self.chat_history.append(
            ChatTurn(
                domain=domain,
                role=role,
                text=text,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        )
        if len(self.chat_history) > self.MAX_CHAT_HISTORY:
            self.chat_history = self.chat_history[-self.MAX_CHAT_HISTORY :]

    def recent_chat_context(self, domain: str, limit: int = 6) -> str:
        """Compact natural-language block of the last `limit` chat turns for
        one domain on this farm, for splicing into an LLM prompt alongside
        to_prompt_context(). Flat string, matching llm_client.generate()'s
        single-prompt-string API -- no message-list/session object. Serves
        both within-session and cross-session recall identically, since
        chat_history has no session-boundary tracking (see ChatTurn)."""
        turns = [t for t in self.chat_history if t.domain == domain][-limit:]
        if not turns:
            return ""
        lines = [f"  {t.role}: {t.text}" for t in turns]
        return "Recent conversation in this section:\n" + "\n".join(lines)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_prompt_context(self) -> str:
        """Compact natural-language summary for injecting into LLM prompts."""
        w = self.current_weather
        location_line = f"Location: {self.location or 'unknown'}"
        if self.country_code:
            location_line += f" ({self.country_code})"
        lines = [location_line]
        if w.temp_c is not None:
            lines.append(
                f"Current weather: {w.temp_c}C, {w.humidity_pct}% humidity, "
                f"{w.rainfall_recent_mm}mm rain recently, "
                f"{w.rainfall_forecast_7day_mm}mm forecast over next 7 days, "
                f"conditions: {w.condition}"
            )
        if self.crops_grown:
            lines.append(f"Crops grown: {', '.join(self.crops_grown)}")
        if self.recent_symptoms_reported:
            recent = self.recent_symptoms_reported[-3:]
            symptom_lines = [
                f"  - {s.crop}: {s.symptoms}" + (f" (diagnosis: {s.diagnosis})" if s.diagnosis else "")
                for s in recent
            ]
            lines.append("Recent symptom reports:\n" + "\n".join(symptom_lines))
        if self.regional_disease_notes:
            lines.append("Regional disease notes: " + "; ".join(self.regional_disease_notes))
        return "\n".join(lines)

    @classmethod
    def _from_dict(cls, data: dict) -> "FarmProfile":
        weather = WeatherSnapshot(**data.get("current_weather", {}))
        symptoms = [SymptomReport(**s) for s in data.get("recent_symptoms_reported", [])]
        chat_history = [ChatTurn(**c) for c in data.get("chat_history", [])]
        return cls(
            name=data.get("name", "Farm 1"),
            location=data.get("location", ""),
            country_code=data.get("country_code", ""),
            location_confirmed=data.get("location_confirmed", False),
            current_weather=weather,
            crops_grown=data.get("crops_grown", []),
            recent_symptoms_reported=symptoms,
            regional_disease_notes=data.get("regional_disease_notes", []),
            chat_history=chat_history,
        )


@dataclass
class FarmState:
    """Container for all of a farmer's farms plus which one is active.

    Kept as a thin wrapper rather than folding farms into a plain list
    everywhere else in the codebase, so `FarmState.load`/`.save` stay the
    single persistence boundary (unchanged from before multi-farm support).
    """

    farms: list[FarmProfile] = field(default_factory=list)
    # Index into `farms`, or None when nothing is active yet (zero farms,
    # or a multi-farm farmer who hasn't said which one they mean this
    # exchange -- see farmer_server.py's farm-disambiguation logic).
    active_farm_index: int | None = None
    # The farmer's whole visible conversation, across every farm and every
    # browser tab/session -- see TranscriptEntry's docstring for why this
    # exists separately from each farm's own chat_history. Capped the same
    # way chat_history is, for the same reason (bounded file growth for an
    # otherwise unbounded, always-appending log).
    transcript: list[TranscriptEntry] = field(default_factory=list)

    MAX_TRANSCRIPT = 200

    def add_transcript_entry(self, kind: str, domain: str | None, text: str) -> None:
        self.transcript.append(
            TranscriptEntry(kind=kind, domain=domain, text=text, timestamp=datetime.now(timezone.utc).isoformat())
        )
        if len(self.transcript) > self.MAX_TRANSCRIPT:
            self.transcript = self.transcript[-self.MAX_TRANSCRIPT :]

    @property
    def active_farm(self) -> FarmProfile | None:
        if self.active_farm_index is None:
            return None
        if 0 <= self.active_farm_index < len(self.farms):
            return self.farms[self.active_farm_index]
        return None

    def add_farm(self, name: str, location: str = "", location_confirmed: bool = False) -> int:
        """Create a new farm, make it active, and return its index."""
        self.farms.append(FarmProfile(name=name, location=location, location_confirmed=location_confirmed))
        self.active_farm_index = len(self.farms) - 1
        return self.active_farm_index

    def set_active(self, index: int) -> None:
        if 0 <= index < len(self.farms):
            self.active_farm_index = index

    def to_dict(self) -> dict:
        return {
            "farms": [f.to_dict() for f in self.farms],
            "active_farm_index": self.active_farm_index,
            "transcript": [asdict(t) for t in self.transcript],
        }

    @classmethod
    def _from_dict(cls, data: dict) -> "FarmState":
        farms = [FarmProfile._from_dict(f) for f in data.get("farms", [])]
        transcript = [TranscriptEntry(**t) for t in data.get("transcript", [])]
        return cls(farms=farms, active_farm_index=data.get("active_farm_index"), transcript=transcript)


# Sentinel key the pre-multi-farmer flat farm_state.json is migrated under
# (see FarmStore.load) -- a placeholder until some real farmer_id claims it.
LEGACY_FARMER_KEY = "_legacy_unclaimed"


@dataclass
class FarmStore:
    """All farmers' data, keyed by farmer_id (a UUID the browser generates
    once and keeps in localStorage -- see SESSION_ID's sibling FARMER_ID in
    farmer.html). Each farmer gets their own independent FarmState, so
    "which farm?" resolution, farm lists and everything else that used to
    read one shared global FarmState now reads one scoped to whoever is
    actually asking.

    REAL BUG FOUND AND FIXED (2026-09-27, reported live: testing from a
    second phone as a separate user, then checking the first phone,
    showed the second person's farm): before this, the whole app had
    exactly one FarmState, shared by every visitor to the deployed URL --
    SessionState (added earlier) only scoped which farm a given browser
    TAB's conversation was about, never which farms existed for which
    person, so every farmer's farms lived in the same list.
    """

    farmers: dict[str, FarmState] = field(default_factory=dict)

    def get(self, farmer_id: str) -> FarmState:
        state = self.farmers.get(farmer_id)
        if state is None:
            # A brand-new real farmer_id's very first request claims
            # whatever pre-multi-farmer data is still sitting unclaimed
            # under LEGACY_FARMER_KEY (per the user's explicit choice:
            # "migrate it to whichever browser visits first after
            # deploying") -- but only once: after this, the key is gone,
            # so no later farmer_id can ever steal it too.
            if farmer_id != LEGACY_FARMER_KEY:
                state = self.farmers.pop(LEGACY_FARMER_KEY, None)
            state = state or FarmState()
            self.farmers[farmer_id] = state
        return state

    def save(self, path: str | Path) -> None:
        data = {"farmers": {fid: fs.to_dict() for fid, fs in self.farmers.items()}}
        Path(path).write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "FarmStore":
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        if "farmers" in data:
            return cls(farmers={fid: FarmState._from_dict(fs) for fid, fs in data["farmers"].items()})
        # Pre-multi-farmer flat format ({"farms": [...], "active_farm_index":
        # ...}) -- park it under the legacy key so the first real farmer_id
        # to ask for state claims it (see get()), rather than losing
        # whatever farms were already saved before this feature existed.
        if "farms" in data:
            return cls(farmers={LEGACY_FARMER_KEY: FarmState._from_dict(data)})
        return cls()
