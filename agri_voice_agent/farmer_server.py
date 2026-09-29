"""Farmer-facing dashboard server: one chat, three agents underneath.

Separate from dashboard_server.py (the technical/judge-facing view over
VoiceAgentLoop's continuous mic + wakeword pipeline, which uses its own
"Hey Green" wakeword -- see wakeword/router.py -- and is left untouched
by this file's own single-chat routing).

This server used to make the farmer click a Weather/Crop/Plant button
before every question (mirroring the wakeword concept in click form). In
practice a farmer chatting naturally forgets to re-click when their topic
shifts mid-conversation -- "do you think we have rain next week" while the
Plant button was still active would silently go to the wrong agent. So the
farmer-facing side is now a SINGLE chat: every message runs through
intent.py's keyword detection (then an LLM classifier with recent turns as
context) to pick the right agent automatically (see route_message() below).
A message neither can place gets "Sorry, I didn't catch that" rather than a
guessed answer; a Plant follow-up answer always stays with Plant.

Two ways a farmer's utterance reaches a domain agent:
  1. POST /chat -- typed text, works everywhere, no API key beyond the
     optional GEMINI_API_KEY for natural phrasing. Fully built and tested.
  2. WS /voice -- browser-captured microphone audio streamed to the
     server, fed into StreamingASR, transcribed text routed the same way
     as typed input. Requires ASSEMBLYAI_API_KEY. Built to the same API
     contract as asr.py, but UNVERIFIED end-to-end: no AssemblyAI key is
     configured in this project yet, so this path has only been exercised
     for construction/import correctness, not a real microphone-to-
     transcript round trip. Test with a real key before relying on it.

Both paths write into the same shared FarmState (loaded/saved at
config.FARM_STATE_PATH) that dashboard_server.py's VoiceAgentLoop also
uses, so a farmer's diagnosis here is visible to the technical dashboard
and vice versa -- one farm list, one state, two front ends.

A farmer can have more than one farm (different fields, can be in
different regions), so farm selection happens on every fresh exchange
(never mid-Plant-diagnosis, same guard as the cross-domain redirect):
  - 0 farms and no location given -- agents still run against an ephemeral,
    unsaved FarmProfile so "what can I grow" works with zero setup; the
    farmer is nudged for a location so it can be saved once given.
  - 0 farms and a location IS given -- that location becomes farm #1
    automatically (default name "Farm 1", renameable later), so the next
    visit doesn't ask again.
  - 1 farm -- used silently, never asked about.
  - 2+ farms -- resolved by an explicit `farm_name` in the request if given
    (e.g. a farmer says "how's the weather on my north field"), otherwise
    the server asks which farm before calling any domain agent, ONCE PER
    BROWSER SESSION (see SessionState below) -- picking a farm by voice/chat
    is the only thing that answers a question against it; clicking a farm
    in the sidebar only changes which one the sidebar highlights/shows.
See resolve_active_farm() below for the actual decision logic.

Every browser tab gets its own SessionState (active domain lock, which farm
this conversation resolved to, any pending location question), keyed by a
client-generated session_id sent with every /chat and /voice call. Before
this, all of that lived in module-level globals shared by every tab and
every visit forever -- a farm selected by clicking, or resolved from a
single ambiguous question days ago, silently applied to every later
question from anyone, and two tabs open at once bled into each other's
plant diagnosis and active domain. `FarmState.farms` itself (the actual
saved farm data) stays global, as it should -- only the "which one is this
conversation about" selection is now per-session.
"""

from __future__ import annotations

import asyncio
import contextvars
import re
from dataclasses import dataclass, field
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, tts_client
from .asr import StreamingASR
from .domains.crop import CropAgent
from .domains.plant import PlantAgent
from .domains.weather import WeatherAgent
from .farm_state import LEGACY_FARMER_KEY, FarmProfile, FarmState, FarmStore
from .domains.weather import extract_location
from .intent import detect_domain
from .interpreter import interpret

STATIC_DIR = Path(__file__).resolve().parent / "static"
WAKEWORD_MODELS_DIR = config.WAKEWORD_MODELS_DIR

DOMAIN_AGENTS = {
    "weather": WeatherAgent,
    "crop": CropAgent,
    "plant": PlantAgent,
}

# Same distinction as main.py: Plant holds a multi-turn session (up to 2
# follow-up questions) via PlantSession; Weather/Crop answer in one shot.
MULTI_TURN_DOMAINS = {"plant"}

app = FastAPI(title="Farmer Dashboard")

# Serves whatever .onnx wakeword models actually exist (dropped in by the
# user, see wakeword/router.py's module docstring -- this project has no
# training pipeline of its own) to the browser for client-side detection
# via onnxruntime-web. The directory is created empty at project scaffold
# time (only a .gitkeep) so this mount never 404s the whole app even
# before any model file is provided -- individual file requests 404
# normally until their .onnx actually exists, which /capabilities'
# wakeword_models field lets the frontend check for up front.
WAKEWORD_MODELS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/wakeword-models", StaticFiles(directory=str(WAKEWORD_MODELS_DIR)), name="wakeword-models")

@dataclass
class SessionState:
    """Everything about "who we're talking to and about what" that must be
    scoped to ONE browser tab's conversation, not shared globally -- see
    the module docstring. Looked up by session_id (a UUID the frontend
    generates once per page load and sends with every request), created on
    first use, and never persisted to disk: a reload is a new session on
    purpose, which is what makes farm selection re-ask itself as designed.
    """

    # Which domain the last message in THIS session was routed to -- starts
    # on "crop" since picking what to plant is the most common zero-context
    # opener and needs no location/weather data to answer. Used the same way
    # the old module-level _current_domain was: to keep a message with no
    # clear keyword match on-topic, and to lock onto "plant" mid-diagnosis.
    current_domain: str = "crop"
    # Which farm THIS session has resolved its questions to, once resolved
    # (via an unambiguous farm_name, or by answering the "which farm?"
    # question) -- None until then, which is what makes the ambiguous-farm
    # question fire again at the start of every new session.
    active_farm_index: int | None = None
    # (domain, original question text) being held while this session waits
    # for a location reply (see _answer()'s pending-location branch).
    # Started out weather-only ("what's the weather" with no known
    # location); now also used for crop questions, since crop suitability
    # reads farm.to_prompt_context()'s climate/country data too and used to
    # just answer generically instead of asking -- see the 2026-09-27
    # "answers a generic list instead of asking for location" bug.
    pending_location_question: tuple[str, str] | None = None
    # (domain, original question text) being held while this session waits
    # to be told WHICH farm the question is about -- set whenever
    # resolve_active_farm() returns ambiguous_farm_names, answered as soon
    # as the farmer names one, by voice or by tapping the picker (which
    # just resends the original text with farm_name set, bypassing this).
    pending_farm_question: tuple[str, str] | None = None
    # Index of a just-created farm waiting for its location, asked as a
    # follow-up right after "add a farm" with no location given -- see
    # _handle_farm_management()'s add-farm branch. Checked BEFORE
    # pending_location_question in _answer() (more specific, must win): the
    # next reply is applied to this farm's location directly, not
    # forwarded to a weather agent that would answer with a forecast
    # instead of saving anything.
    pending_new_farm_location: int | None = None
    # Index of a farm waiting to be told its NEW location -- set when the
    # farmer asks to change a farm's location without giving the
    # destination in the same message ("update my farm's location", no
    # "to X"). REAL BUG FOUND AND FIXED (2026-09-30, reported live: the
    # assistant asked "which town?", the farmer answered, it replied "I've
    # updated your farm's location to X" -- but the sidebar still showed
    # the OLD location). Root cause: _match_relocate_farm()/_RELOCATE_FARM_RE_*
    # both require "to LOCATION" in the SAME message, so a bare "update my
    # farm's location" matched neither and fell through past all
    # deterministic farm-management handling straight to ordinary domain
    # routing -- which handed it to an LLM-phrased agent reply. That agent
    # has no tool to actually change farm.location, so "which town or
    # area...", and later "I've updated it to X", were both pure LLM
    # phrasing with NO real state change behind them -- a direct violation
    # of this project's "deterministic logic decides, LLM only phrases"
    # rule, and confusing/untrustworthy besides. This field, handled the
    # same way pending_new_farm_location is (checked in _answer() before
    # generic routing, the reply applied directly to farm.location), makes
    # the same two-step "which town?" / "<reply>" exchange actually work.
    pending_relocate_farm: int | None = None
    # (farm index, farm name) awaiting a yes/no reply to "delete FARM? this
    # can't be undone" -- see _handle_farm_management(). Name is stored
    # alongside the index so a stale confirmation (the farm list changed
    # underneath, e.g. from another tab, since the question was asked)
    # is detected rather than deleting whatever now happens to sit at
    # that index.
    pending_farm_deletion: tuple[int, str] | None = None
    # (location,) held while waiting for a unique name for a NEW farm --
    # the name the farmer explicitly gave collided (case-insensitively)
    # with an existing farm. A 1-tuple (not a bare `str | None`) so an
    # empty-string location ("add a farm called Home" with no place) is
    # distinguishable from "nothing pending" -- see _add_farm_reply().
    # Farm names are now kept unique across a farmer's whole list
    # (2026-09-28, explicit user choice).
    pending_new_farm_name: tuple[str] | None = None
    # (farm index, old name) held while waiting for a unique REPLACEMENT
    # name after a rename collided with a DIFFERENT existing farm.
    # Renaming a farm to its own current name is a harmless no-op, not a
    # collision -- see _name_collides()'s exclude_idx.
    pending_rename: tuple[int, str] | None = None
    # Per-session Plant diagnostic conversation -- PlantAgent's own
    # _active_sessions dict is keyed by whatever session_id we pass it, so
    # this just needs to consistently pass the SAME id for a given browser
    # tab instead of every call defaulting to "default".
    session_id: str = ""
    # Every exchange in this tab, as (role, text) -- including replies with
    # no farm attached (farm-list answers, clarifications), which the
    # per-farm chat_history never recorded. That gap is why follow-ups lost
    # their context after a few turns; this is what interpret() reads.
    history: list[tuple[str, str]] = field(default_factory=list)


_sessions: dict[str, SessionState] = {}


def _get_session(session_id: str | None) -> SessionState:
    """Session state for one browser tab. A missing/empty id (a client that
    predates this feature, or a direct API call) falls back to a single
    shared "legacy" session -- old behavior, not a crash -- rather than a
    fresh one per call, which would ask "which farm?" on every message."""
    key = session_id or "_legacy"
    session = _sessions.get(key)
    if session is None:
        session = SessionState(session_id=key)
        _sessions[key] = session
    return session


# LEGACY_FARMER_KEY (see farm_state.py) is used as the fallback for a
# missing/empty farmer_id -- a client that predates this feature, or a
# direct API call -- so those callers keep seeing whatever farms already
# existed before per-farmer scoping shipped, same fallback philosophy as
# _get_session()'s "_legacy" session key above.
_farm_store = FarmStore.load(config.FARM_STATE_PATH)

# The real fix for "the farms should be farmer specific" (reported live,
# 2026-09-27: testing from a second phone as a separate user, then
# checking back on the first phone, showed the second person's farm). Every
# function below still reads/writes a bare `_farm_state` exactly as before
# -- unlike SessionState (which only ever scoped which farm a given
# browser TAB's conversation was about), the module-level global here used
# to be ONE FarmState shared by literally every visitor. Rather than thread
# a `farm_state` parameter through every one of those ~20 functions
# individually, `_farm_state` is now a request-scoped ContextVar: each
# request handler resolves the caller's real FarmState via
# `_use_farm_state(farmer_id)` right at its entry point (see _answer(),
# _handle_voice_transcript(), and the /farm_state, /farms endpoints below),
# and every existing `_farm_state.foo` reference transparently reads
# whichever FarmState that request bound, via _FarmStateProxy.__getattr__.
# Concurrency is safe because ContextVar is per-task/per-thread: FastAPI
# runs each request's sync code in its own asyncio.to_thread worker, and a
# contextvars snapshot is copied into that thread, not shared across it.
_current_farm_state: contextvars.ContextVar[FarmState] = contextvars.ContextVar("_current_farm_state")


class _FarmStateProxy:
    """Forwards every attribute access to whichever FarmState the current
    request bound via _use_farm_state() -- lets every pre-existing
    `_farm_state.foo` call site below keep working unchanged after
    `_farm_state` stopped being a single shared global."""

    def __getattr__(self, name: str):
        return getattr(_current_farm_state.get(), name)

    def __setattr__(self, name: str, value) -> None:
        setattr(_current_farm_state.get(), name, value)


_farm_state = _FarmStateProxy()


def _use_farm_state(farmer_id: str | None) -> FarmState:
    """Bind `_farm_state` (see _FarmStateProxy above) to this farmer's own
    FarmState for the rest of the current request. Call once, as early as
    possible, in every request handler that touches farm data."""
    state = _farm_store.get(farmer_id or LEGACY_FARMER_KEY)
    _current_farm_state.set(state)
    return state


_agents: dict[str, object] = {}
for _name, _cls in DOMAIN_AGENTS.items():
    try:
        _agents[_name] = _cls()
    except RuntimeError as exc:
        print(f"[farmer_server] '{_name}' domain agent unavailable: {exc}")


def _domain_conversation_done(domain: str, session_id: str) -> bool:
    """Mirrors main.py's VoiceAgentLoop._domain_conversation_done -- True
    once a multi-turn domain (Plant) has reached a final diagnosis for its
    current session, so the frontend knows whether to keep prompting for
    another follow-up answer or the exchange is complete."""
    agent = _agents.get(domain)
    if isinstance(agent, PlantAgent):
        return agent.is_done(session_id)
    return True


def route_message(text: str, session: SessionState) -> tuple[str | None, bool, bool]:
    """Pick which domain this message belongs to. Returns (domain,
    is_fresh_exchange, switched); domain is None when the message is
    unclear and the farmer should be asked to repeat it.

    `is_fresh_exchange` is False only when continuing the currently-active
    multi-turn Plant conversation -- the farmer's answer to a follow-up
    question (e.g. "the whole plant, not just one branch") must never be
    re-routed. An unambiguous keyword match to a DIFFERENT domain (e.g.
    "how is the weather" partway through a symptom Q&A) still redirects,
    though -- abandoning the plant session -- since that's a genuine topic
    change, not a follow-up answer; only a message with no clear keyword
    match (which is what a real follow-up answer looks like) stays locked
    to plant. Otherwise keywords decide; no match returns None and the
    caller falls back to interpret(). There is deliberately no fallback to
    the previously active domain: that used to answer garbled or echoed
    transcripts ("How can I help you today.") with a weather report.

    `switched` is True only when this message moved the chat to a
    different domain -- used for a small "switched to X" note in the UI.
    """
    mid_plant_conversation = session.current_domain == "plant" and not _domain_conversation_done("plant", session.session_id)
    if mid_plant_conversation:
        redirect = detect_domain(text)
        if redirect is None or redirect == "plant":
            return "plant", False, False
        _agents["plant"].abandon(session.session_id)
        session.current_domain = redirect
        return redirect, True, True

    # No keyword match -> None, and _answer() hands the message to
    # interpret() with the conversation as context.
    detected = detect_domain(text)
    if detected is None:
        return None, True, False
    previous = session.current_domain
    session.current_domain = detected
    return detected, True, detected != previous


def _find_farm_by_name(name: str) -> int | None:
    lowered = name.strip().lower()
    for i, f in enumerate(_farm_state.farms):
        if f.name.strip().lower() == lowered:
            return i
    return None


def _name_collides(name: str, exclude_idx: int | None = None) -> bool:
    """True if `name` (case-insensitive) already belongs to some OTHER
    farm -- `exclude_idx` lets a rename check against every farm except
    the one actually being renamed, so "rename Home to Home" is a
    harmless no-op, not flagged as a collision with itself."""
    lowered = name.strip().lower()
    return any(
        i != exclude_idx and f.name.strip().lower() == lowered for i, f in enumerate(_farm_state.farms)
    )


def _unique_default_name() -> str:
    """"Farm N" for the next N that isn't already taken -- used only when
    the farmer didn't give a name at all ("add a farm"), so an
    auto-generated default never collides either (e.g. after "Farm 2" was
    deleted and a new farm auto-names into that same slot while a
    differently-numbered "Farm 2" still exists from some other add)."""
    n = len(_farm_state.farms) + 1
    while _name_collides(f"Farm {n}"):
        n += 1
    return f"Farm {n}"


def _find_farm_in_speech(text: str) -> int | None:
    """Looser match for a farm name spoken/typed inside a full sentence
    ("it's about Farm 1", "the Colombo one") rather than passed as the
    exact structured farm_name field -- used only for answering the
    "which farm?" question by voice. Matches the farm's own name OR its
    location as a whole-word substring; if more than one farm matches
    (e.g. two farms share a word in their name), treated as still
    unresolved rather than guessing."""
    lowered = text.lower()
    matches = [
        i
        for i, f in enumerate(_farm_state.farms)
        if (f.name and re.search(r"\b" + re.escape(f.name.strip().lower()) + r"\b", lowered))
        or (f.location and re.search(r"\b" + re.escape(f.location.split(",")[0].strip().lower()) + r"\b", lowered))
    ]
    return matches[0] if len(matches) == 1 else None


# Reused (not recreated) across calls with zero farms / an unresolved
# ambiguous selection, so a multi-turn Plant conversation started before
# any farm exists keeps writing its symptom report onto the SAME object
# PlantSession cached via set_farm() on turn 1 -- a fresh FarmProfile every
# call would make farm.add_symptom_report() on the final turn write onto a
# throwaway object and silently lose the report. Not persisted to disk;
# becomes moot the moment a real farm exists (all other resolve_active_farm
# branches return a `_farm_state.farms[...]` entry instead).
_scratch_farm = FarmProfile(name="", location_confirmed=False)


def resolve_active_farm(
    session: SessionState, farm_name: str | None, location: str | None
) -> tuple[FarmProfile, bool, list[str] | None]:
    """Decide which farm THIS SESSION's exchange is about, per the module
    docstring's rules. Returns (farm, is_ephemeral, ambiguous_farm_names).

    `is_ephemeral` is True when the returned FarmProfile is a scratch
    object not stored in `_farm_state.farms` -- the zero-farms-yet case, so
    "what can I grow" works before any farm exists. `ambiguous_farm_names`
    is non-None only when there are 2+ farms and neither `farm_name` nor
    this session's own already-resolved farm disambiguates which one is
    meant; callers must then skip calling any domain agent and ask the
    farmer to pick. Once resolved, the choice is remembered on `session`
    (not `_farm_state`) so it applies for the rest of this browser tab's
    conversation but a NEW tab/session is asked again -- see the module
    docstring. `_farm_state.set_active()` is still called alongside, purely
    so the sidebar's own "active" highlight reflects the most recent
    selection from any session; it never feeds back into routing.
    """
    if farm_name:
        idx = _find_farm_by_name(farm_name)
        if idx is not None:
            session.active_farm_index = idx
            _farm_state.set_active(idx)
            return _farm_state.farms[idx], False, None
        # Named a farm that doesn't exist -- fall through to normal
        # resolution rather than silently ignoring what they said.

    if len(_farm_state.farms) == 0:
        if location:
            # First-ever confirmed location becomes farm #1 automatically,
            # so the farmer is never asked to explicitly "create a farm" --
            # see the module docstring's auto-save rule.
            idx = _farm_state.add_farm("Farm 1", location=location, location_confirmed=True)
            session.active_farm_index = idx
            return _farm_state.farms[idx], False, None
        # No farms, no location yet -- still usable anonymously (e.g. crop
        # suitability without weather), via a scratch, unsaved profile.
        return _scratch_farm, True, None

    if len(_farm_state.farms) == 1:
        session.active_farm_index = 0
        _farm_state.set_active(0)
        return _farm_state.farms[0], False, None

    # 2+ farms: this SESSION already resolving one earlier still counts (so
    # a farmer doesn't get re-asked every single message within one visit),
    # but a fresh session with nothing resolved yet is genuinely ambiguous.
    idx = session.active_farm_index
    if idx is not None and 0 <= idx < len(_farm_state.farms):
        return _farm_state.farms[idx], False, None

    return _scratch_farm, True, [f.name for f in _farm_state.farms]


class ChatIn(BaseModel):
    text: str
    crop: str | None = None
    # Only meaningful for the weather domain -- see resolve_active_farm().
    # Lets the farmer set/change where a farm actually is instead of every
    # request silently using config.DEFAULT_LOCATION.
    location: str | None = None
    # Which farm this question is about, when the farmer has more than one
    # (e.g. picked from the farm-disambiguation prompt, or the Farms
    # section's selector). Also accepted as a spoken/typed farm name.
    farm_name: str | None = None
    # A UUID this browser tab generated on page load -- see SessionState.
    # Optional so old/direct API callers still work (falls back to a single
    # shared legacy session, matching the pre-session-scoping behavior).
    session_id: str | None = None
    # A UUID this browser/device generated once and persisted (localStorage,
    # not per-tab like session_id above) -- scopes which farms exist for
    # this request, see FarmStore/_use_farm_state(). Optional so old/direct
    # API callers still work (falls back to LEGACY_FARMER_KEY, i.e. whatever
    # farms existed before per-farmer scoping shipped).
    farmer_id: str | None = None


class ChatOut(BaseModel):
    domain: str
    response: str
    done: bool
    farm_state: dict
    # True when this message's own wording caused the chat to switch
    # agents from whatever was active before -- see route_message() in
    # intent.py. The frontend uses this to show a small "switched to X"
    # note so the farmer can see why the topic changed, without having to
    # click anything themselves.
    switched: bool = False
    # True when a weather question was answered using a fallback/default
    # location rather than one the farmer actually gave -- the frontend
    # uses this to prompt for a real location instead of silently reusing
    # config.DEFAULT_LOCATION forever.
    needs_location: bool = False
    # Non-None only when 2+ farms exist and it's unclear which one this
    # question is about -- no domain agent was called this turn; the
    # frontend should ask the farmer to pick one of these names and resend
    # with `farm_name` set.
    ambiguous_farms: list[str] | None = None
    # True when this reply was a farewell -- the frontend ends the current
    # voice conversation (stops listening for a follow-up, back to
    # wakeword-only) instead of waiting out the usual follow-up window.
    end_conversation: bool = False


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "farmer.html")


@app.get("/wakeword-test")
async def wakeword_test() -> FileResponse:
    """Standalone wakeword-detection test page -- no chat, no ASR, no API
    keys needed. Exists specifically to test the client-side openWakeWord
    pipeline in isolation (does saying "Hey Green" out loud actually cross
    the 0.2 threshold) without ASSEMBLYAI_API_KEY gating the farmer
    dashboard's own wake-toggle button. See static/wakeword_test.html."""
    return FileResponse(STATIC_DIR / "wakeword_test.html")


@app.get("/capabilities")
async def capabilities() -> dict:
    """Tells the frontend what's actually usable right now, so it can show
    the mic button only when a real voice round-trip is possible instead
    of offering a control that would just fail.

    `wakeword_models` reports which wakewords have a COMPLETE, runnable
    detection chain -- not just their own classifier .onnx but also the
    two shared openWakeWord feature-extraction models (melspectrogram.onnx,
    embedding_model.onnx) every classifier depends on (see farmer.html's
    voice module: raw audio -> melspectrogram -> embedding -> classifier,
    each a separate .onnx file). A classifier file alone can't detect
    anything -- its input is a stack of 16 embeddings, not raw audio -- so
    reporting true without the shared models present would let the
    frontend start a wakeword loop that can never actually fire. All three
    files are served to the browser at /wakeword-models/<name>.onnx via
    the StaticFiles mount below. Wakeword listening additionally needs
    mic_available (ASSEMBLYAI_API_KEY) since detecting the wakeword is only
    useful if the follow-up speech can then actually be transcribed.

    Only "field" (the "Hey Green" wakeword) is listed here -- down from
    ("field", "plant") as of 2026-09-28, explicit user choice to use a
    single wakeword covering all three domains (see intent.py's
    resolve_field_domain(), which now resolves "Hey Green" to weather,
    crop, OR plant instead of only ever weather/crop). farmer.html's
    loadWakewordModels() already just loads whatever names show up here
    with a value of True, so this one-line change is what actually turns
    off loading/scoring a "plant" classifier client-side -- no frontend
    code needed touching for that part.
    """
    shared_models_present = (WAKEWORD_MODELS_DIR / "melspectrogram.onnx").exists() and (
        WAKEWORD_MODELS_DIR / "embedding_model.onnx"
    ).exists()
    return {
        "mic_available": bool(config.ASSEMBLYAI_API_KEY),
        "phrasing_available": bool(config.GEMINI_API_KEY),
        "domains_available": {name: name in _agents for name in DOMAIN_AGENTS},
        "wakeword_models": {
            name: shared_models_present and (WAKEWORD_MODELS_DIR / f"{name}.onnx").exists()
            for name in ("field",)
        },
        # elevenlabs-tts branch only -- lets farmer.html know whether to
        # even attempt the cloud-voice path before falling back to the
        # browser's own free speechSynthesis, same "never offer a control
        # that would just fail" pattern every other capability here
        # already follows.
        "cloud_tts_available": bool(config.ELEVENLABS_API_KEY and config.ELEVENLABS_VOICE_ID),
    }


@app.get("/farm_state")
async def get_farm_state(farmer_id: str | None = None) -> dict:
    _use_farm_state(farmer_id)
    return _farm_state.to_dict()


class FarmOut(BaseModel):
    index: int
    name: str
    location: str
    location_confirmed: bool
    active: bool


@app.get("/farms", response_model=list[FarmOut])
async def list_farms(farmer_id: str | None = None) -> list[FarmOut]:
    _use_farm_state(farmer_id)
    return [
        FarmOut(
            index=i,
            name=f.name,
            location=f.location,
            location_confirmed=f.location_confirmed,
            active=(i == _farm_state.active_farm_index),
        )
        for i, f in enumerate(_farm_state.farms)
    ]


class AddFarmIn(BaseModel):
    name: str
    location: str | None = None
    farmer_id: str | None = None


@app.post("/farms", response_model=FarmOut)
async def add_farm(body: AddFarmIn) -> FarmOut:
    """Explicitly add a farm from the Farms section UI (as opposed to the
    auto-save-as-"Farm 1" path in resolve_active_farm(), which only fires
    for the very first farm)."""
    _use_farm_state(body.farmer_id)
    name = body.name.strip() or f"Farm {len(_farm_state.farms) + 1}"
    idx = _farm_state.add_farm(name, location=body.location or "", location_confirmed=bool(body.location))
    _farm_store.save(config.FARM_STATE_PATH)
    f = _farm_state.farms[idx]
    return FarmOut(index=idx, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=True)


@app.post("/farms/{index}/select", response_model=FarmOut)
async def select_farm(index: int, farmer_id: str | None = None) -> FarmOut:
    _use_farm_state(farmer_id)
    if not (0 <= index < len(_farm_state.farms)):
        raise ValueError(f"No farm at index {index}")
    _farm_state.set_active(index)
    _farm_store.save(config.FARM_STATE_PATH)
    f = _farm_state.farms[index]
    return FarmOut(index=index, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=True)


class UpdateFarmIn(BaseModel):
    name: str | None = None
    location: str | None = None
    farmer_id: str | None = None


@app.patch("/farms/{index}", response_model=FarmOut)
async def update_farm(index: int, body: UpdateFarmIn) -> FarmOut:
    """Rename a farm and/or change its saved location after it's already
    been added -- separate from POST /farms (creates a new one) and
    POST /farms/{index}/select (switches which is active). Either field
    may be omitted to leave it unchanged."""
    _use_farm_state(body.farmer_id)
    if not (0 <= index < len(_farm_state.farms)):
        raise ValueError(f"No farm at index {index}")
    f = _farm_state.farms[index]
    if body.name is not None:
        name = body.name.strip()
        if name:
            f.name = name
    if body.location is not None:
        location = body.location.strip()
        f.location = location
        f.location_confirmed = bool(location)
    _farm_store.save(config.FARM_STATE_PATH)
    return FarmOut(index=index, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=(index == _farm_state.active_farm_index))


def _delete_farm(index: int) -> None:
    """Remove a farm and keep every session's (and the global display's)
    active_farm_index pointing at the right farm afterward -- every one of
    them is just an index into this same list, so removing an entry must
    shift or clear every reference to it consistently, or a farm removed
    from one browser tab (or via the sidebar) would silently leave another
    tab pointed at the wrong farm, or one past the end of the list."""
    _farm_state.farms.pop(index)
    if _farm_state.active_farm_index is not None:
        if _farm_state.active_farm_index == index:
            _farm_state.active_farm_index = None
        elif _farm_state.active_farm_index > index:
            _farm_state.active_farm_index -= 1
    for other in _sessions.values():
        if other.active_farm_index is None:
            continue
        if other.active_farm_index == index:
            other.active_farm_index = None
        elif other.active_farm_index > index:
            other.active_farm_index -= 1
    _farm_store.save(config.FARM_STATE_PATH)


@app.delete("/farms/{index}")
async def delete_farm(index: int, farmer_id: str | None = None) -> dict:
    _use_farm_state(farmer_id)
    if not (0 <= index < len(_farm_state.farms)):
        raise ValueError(f"No farm at index {index}")
    _delete_farm(index)
    return {"ok": True}


@app.delete("/conversation")
async def clear_conversation(farmer_id: str | None = None) -> dict:
    """"Clear chat" button (farmer.html) -- resets the visible transcript
    (see TranscriptEntry) and every farm's own chat_history (the recent-
    turns context crop.py/plant.py splice into their prompts), so a
    cleared conversation actually starts fresh rather than the agents
    still quietly recalling turns the farmer just asked to forget. Does
    NOT touch farms, their weather/crops_grown/recent_symptoms_reported,
    or regional_disease_notes -- this clears the CONVERSATION, not the
    farm data those turns happened to produce."""
    _use_farm_state(farmer_id)
    _farm_state.transcript = []
    for f in _farm_state.farms:
        f.chat_history = []
    _farm_store.save(config.FARM_STATE_PATH)
    return {"ok": True}


class SpeakIn(BaseModel):
    text: str


# elevenlabs-tts branch only. farmer.html's speak()/speakAndWait() call
# this first (only when /capabilities said cloud_tts_available) and fall
# back to the browser's own speechSynthesis on any failure -- a 503 here
# is the expected, handled shape of "not configured/request failed", not
# a bug, so the frontend must treat it as "use the free fallback" rather
# than surfacing an error to the farmer over a nice-to-have.
@app.post("/speak")
async def speak(body: SpeakIn) -> Response:
    try:
        audio = await asyncio.to_thread(tts_client.synthesize_speech, body.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return Response(content=audio, media_type="audio/mpeg")


class ResolveLocationIn(BaseModel):
    # GPS fix from the browser's navigator.geolocation, when the farmer
    # granted permission. Omitted (both None) triggers the IP-based
    # fallback below.
    lat: float | None = None
    lon: float | None = None


class ResolveLocationOut(BaseModel):
    location: str | None
    source: str  # "gps" | "ip" | "unavailable"


@app.post("/resolve_location", response_model=ResolveLocationOut)
async def resolve_location(body: ResolveLocationIn, request: Request) -> ResolveLocationOut:
    """Auto-detect a location so a farmer doesn't have to type one for
    their first farm. GPS first (device-accurate, needs the browser's
    permission prompt), then IP-geolocation as a same-page fallback if GPS
    was denied or unsupported -- coarser (city-level, via the request's
    public IP) but needs no permission and never blocks the farmer from
    getting *some* auto-filled location.

    This only *resolves a name*; it does not create or modify any farm --
    the frontend still runs it through /chat (or /farms) with the
    resolved name, so the existing farm-creation/confirmation bookkeeping
    stays in one place.
    """
    weather_agent = _agents.get("weather")
    if isinstance(weather_agent, WeatherAgent) and body.lat is not None and body.lon is not None:
        try:
            name = weather_agent.reverse_geocode(body.lat, body.lon)
            return ResolveLocationOut(location=name, source="gps")
        except Exception:  # noqa: BLE001 -- fall through to IP-based lookup
            pass

    client_ip = request.client.host if request.client else None
    # Loopback/private addresses (local dev) can't be IP-geolocated -- skip
    # straight to "unavailable" rather than sending a useless lookup.
    if client_ip and not client_ip.startswith(("127.", "10.", "192.168.", "::1")):
        try:
            # ip-api.com's free tier only serves plain HTTP (its HTTPS
            # endpoint requires a paid key) -- fine here since the only data
            # in flight is the request's own public IP and a resulting
            # city/country, not anything sensitive.
            resp = requests.get(f"http://ip-api.com/json/{client_ip}", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "success":
                city = data.get("city", "")
                country = data.get("countryCode", "")
                if city and country:
                    return ResolveLocationOut(location=f"{city},{country}", source="ip")
        except Exception:  # noqa: BLE001 -- IP geolocation is best-effort
            pass

    return ResolveLocationOut(location=None, source="unavailable")


CLARIFY_TEXT = "Sorry, I didn't catch that. Could you say it again?"
ASK_LOCATION_TEXT = "Sure. Which town or area is your farm in?"
LOCATION_NOT_FOUND_TEXT = "Sorry, I couldn't find that place. Which town or city is your farm near?"
GOODBYE_TEXT = "You're welcome! Let me know if you need anything else. Bye!"

# A closing remark, not a real question -- checked before routing so "thank
# you" doesn't get treated as an unclear farming question or (worse)
# accidentally matched to a domain by a stray keyword. Deliberately just a
# fixed phrase list, not an LLM call: a farewell is easy to recognise
# outright and getting this wrong would end a conversation the farmer didn't
# actually mean to end.
_FAREWELL_PHRASES = (
    "thank you", "thanks", "thank u", "thankyou", "that's all", "that is all",
    "that's it", "that is it", "nothing else", "no that's all", "bye", "goodbye",
    "good bye", "see you", "that's everything", "ok thanks", "okay thanks",
    "alright thanks", "all done", "i'm done", "im done", "we're done",
)


def _is_farewell(text: str) -> bool:
    lowered = text.lower().strip(" .!?")
    return lowered in _FAREWELL_PHRASES or any(
        lowered == phrase or lowered.startswith(phrase + " ") or lowered.endswith(" " + phrase)
        for phrase in _FAREWELL_PHRASES
    )


# A mic-check, not a farming question -- REAL BUG FOUND AND FIXED
# (2026-09-27, reported live: "can you hear me" got "sorry, I didn't catch
# that"). Not a farming question, so detect_domain() has no keyword for it
# and an LLM reading it would rightly call it unclear -- technically right,
# but useless to a farmer who's reasonably checking the mic is working, not
# asking to repeat themselves. Same "fixed phrase list, not an LLM call"
# approach as _is_farewell() above -- this is easy to recognise outright.
MIC_CHECK_TEXT = "Yes, I can hear you! What would you like to know?"
_MIC_CHECK_PHRASES = (
    "can you hear me", "can u hear me", "do you hear me", "are you there",
    "are you listening", "is this working", "testing", "test test",
    "hello are you there", "you there",
)


def _is_mic_check(text: str) -> bool:
    lowered = text.lower().strip(" .!?")
    return lowered in _MIC_CHECK_PHRASES or any(
        lowered == phrase or lowered.startswith(phrase + " ") or lowered.endswith(" " + phrase)
        for phrase in _MIC_CHECK_PHRASES
    )


_LOCATION_REPLY_PREFIX = re.compile(
    r"^(?:(?:it'?s|it is|my farm is|the farm is|we'?re|we are|i'?m|i am"
    r"|the\s+(?:\w+\s+)?farm(?:'?s)?\s+location\s+is"
    r"|(?:the\s+)?location\s+is)\s+)?(?:(?:in|at|near|around)\s+)?",
    re.IGNORECASE,
)


def _location_from_reply(text: str) -> str:
    """"It's in Kandy." -> "Kandy"."""
    return _LOCATION_REPLY_PREFIX.sub("", text.strip()).strip(" .!?,")


# Words that show up in an ordinary sentence/question but essentially never
# in a bare place name -- if the reply to "which town is your farm in?"
# contains one of these, it's not actually answering that question (most
# often a farewell or an unrelated new question that slipped past the
# earlier checks, or a mangled ASR transcript), so it shouldn't be sent to
# the geocoder as if it were a location.
_NOT_A_PLACE_WORDS = {
    "thank", "thanks", "please", "sorry", "what", "when", "where", "why",
    "how", "who", "which", "weather", "rain", "temperature", "humidity",
    "plant", "crop", "grow", "sick", "help", "yes", "no", "okay", "ok",
}


def _looks_like_a_place(reply_text: str, stripped_place: str) -> bool:
    """True if a reply to "which town is your farm in?" plausibly names a
    place rather than being something else entirely (a farewell, an
    unrelated question, a garbled transcript) -- a real place name is
    short and doesn't contain ordinary sentence words. Deliberately
    conservative: a false "no" here just re-asks, which is always
    recoverable, whereas a false "yes" silently geocodes nonsense (see the
    build log's 2026-09-27 entry -- this used to accept anything)."""
    if not stripped_place:
        return False
    words = stripped_place.lower().split()
    if len(words) > 4:
        return False
    if "?" in reply_text:
        return False
    return not any(w.strip(".,!?") in _NOT_A_PLACE_WORDS for w in words)


# ---------------------------------------------------------------------------
# Voice/chat farm management (add / rename / relocate / delete a farm) --
# separate from the weather/crop/plant DOMAIN routing above, since these
# commands are never "about" a farm's crops or weather, they're about the
# farm LIST itself. Deterministic regex matching, same philosophy as
# intent.py's keyword routing: a farm add/delete is destructive/persistent
# enough that a hallucinated LLM guess at "did they mean to add a farm"
# would be worse than just not recognizing the command and falling through
# to normal domain routing (which will then say "sorry, I didn't catch
# that" or answer a real question -- never silently do nothing).
# ---------------------------------------------------------------------------

_ADD_FARM_RE = re.compile(
    # A leading "I need to"/"I want to"/"can you"/"let's"/etc. is stripped
    # first (see _match_add_farm) rather than folded in here, so this stays
    # readable; what's left must still start with the command verb.
    # "a"/"another"/"a new"/"one more" all mean the same thing here --
    # REAL BUG FOUND AND FIXED (2026-09-27, reported live: "add another
    # farm" got "sorry, I didn't catch that"): only "a"/"new" were
    # accepted, so "another" -- an entirely ordinary way to ask for a
    # second farm -- fell through this whole matcher.
    r"^(?:add|create|make|set up|start)\s+(?:a\s+new\s+|a\s+|another\s+|one\s+more\s+)?farm\s*"
    r"(?:(?:called|named)\s+(?P<name1>.+?))?"
    r"(?:\s+in\s+(?P<location>.+?))?$",
    re.IGNORECASE,
)
# Natural lead-ins that precede the actual command in ordinary speech --
# "I need to create a farm", "can you add a farm for me", "I'd like to make
# a new farm", "can I add another farm". Stripped before _ADD_FARM_RE is
# tried. REAL BUG FOUND AND FIXED (2026-09-27, reported live): _ADD_FARM_RE
# required the message to START with the command verb, so any natural
# phrasing in front of it ("I need to...", "can I...") meant the whole
# sentence matched nothing at all and silently fell through to normal
# domain routing instead of creating anything.
_ADD_FARM_LEAD_IN_RE = re.compile(
    r"^(?:i\s+(?:need|want|would like|have)\s+to\s+|i'?d\s+like\s+to\s+|"
    r"(?:can|could)\s+(?:you|i)\s+(?:please\s+)?|"
    r"please\s+|let'?s\s+|i\s+want\s+)+",
    re.IGNORECASE,
)
# The captured name here is deliberately NOT stripped of a leading/trailing
# "farm" -- a real farm can genuinely be named "Farm 1" (the app's own
# default auto-generated name!), so "delete Farm 1" must capture "Farm 1"
# whole, not swallow the word "farm" as if it were just a command noun and
# leave "1". _resolve_farm_reference() tries the full captured phrase
# against the real farm list first and only falls back to a stripped
# version if that fails, so this stays permissive without breaking the
# common case.
_DELETE_FARM_RE = re.compile(r"^(?:delete|remove|drop)\s+(?:the\s+)?(?P<name>.+)$", re.IGNORECASE)
_RENAME_FARM_RE = re.compile(r"^rename\s+(?:the\s+)?(?P<old>.+?)\s+to\s+(?P<new>.+)$", re.IGNORECASE)
#   A) "change/set/update [the] location of/for NAME to LOCATION"
#   B) "change/set/update NAME['s] location to LOCATION"
# REAL BUG FOUND AND FIXED (2026-09-29, reported live: "update the
# location of Farm 1 to Jaffna" -- the natural phrasing -- said it would
# but never actually changed anything). The original single regex had
# "location" appear only once in its pattern but required it to satisfy
# BOTH the optional "location of/for" lead-in AND the mandatory "location
# to" before the destination -- so phrasing A consumed "location" in the
# lead-in and left nothing to match the mandatory "location to" later,
# silently failing to match at all (which farmer_server.py's caller then
# reported as a generic "sorry, I didn't catch that", not an error -- easy
# to miss). Split into two patterns, one per phrasing, tried in order.
_RELOCATE_FARM_RE_A = re.compile(
    r"^(?:change|set|update)\s+(?:the\s+)?location\s+(?:of|for)\s+(?P<name>.+?)\s+to\s+(?P<location>.+)$",
    re.IGNORECASE,
)
_RELOCATE_FARM_RE_B = re.compile(
    r"^(?:change|set|update)\s+(?P<name>.+?)(?:'s)?\s+location\s+to\s+(?P<location>.+)$",
    re.IGNORECASE,
)
# Same two phrasings as above, but with NO destination given yet ("update
# my farm's location", "change the location of Farm 1") -- see
# pending_relocate_farm's docstring on SessionState for the bug this
# fixes: without this, the message matched neither RE_A/RE_B (both
# require "to LOCATION") and fell through to an LLM-phrased domain reply
# that could ask a plausible-sounding question but had no way to actually
# apply the answer.
_RELOCATE_NO_DEST_RE = re.compile(
    r"^(?:change|set|update)\s+(?:the\s+)?"
    r"(?:location\s+(?:of|for)\s+(?P<name1>.+?)|(?P<name2>.+?)(?:'s)?\s*location)\s*[.!?]*$",
    re.IGNORECASE,
)
# Filler ways of referring to "the farm we're already talking about"
# rather than naming one -- normalized to "" so _resolve_farm_reference()
# falls back to the session's active farm instead of failing to find a
# farm literally named "my farm".
_GENERIC_FARM_REF = {"my farm", "the farm", "this farm", "that farm", "it"}
# A genuine question, not a command -- "what farms do I have", "what farms
# are there", "list my farms", "how many farms do I have". Added because a
# farmer naturally asking this (or an ASR mangling of it, e.g. "what are my
# phone names" for "what are my farm names") had nothing to answer it --
# it fell through every branch to the generic clarify fallback.
_LIST_FARMS_RE = re.compile(
    r"\b(?:what|which|how many)\s+farms?\b|\blist\s+(?:my\s+)?farms?\b|"
    r"\bmy\s+farms?\s+(?:names?|list)\b|\bfarm\s+names?\b",
    re.IGNORECASE,
)
_CONFIRM_YES_RE = re.compile(r"^(yes|yeah|yep|confirm|do it|go ahead|sure)\b", re.IGNORECASE)
_CONFIRM_NO_RE = re.compile(r"^(no|nope|don'?t|cancel|stop|nevermind|never mind)\b", re.IGNORECASE)


def _clean_farm_phrase(text: str) -> str:
    return text.strip(" .!?,").strip()


def _match_add_farm(text: str) -> tuple[str, str] | None:
    """("I need to create a farm called North Field in Kandy") -> ("North
    Field", "Kandy"). Name defaults to "Farm N" (like the sidebar's own Add
    Farm button) when the farmer didn't give one -- "add a farm in Kandy"
    or even bare "I need to create a farm" alone is still a reasonable,
    actionable command; the missing piece is asked for as a follow-up
    rather than the whole command being rejected."""
    stripped = _ADD_FARM_LEAD_IN_RE.sub("", text.strip())
    m = _ADD_FARM_RE.match(stripped)
    if not m:
        return None
    name = _clean_farm_phrase(m.group("name1") or "")
    location = _clean_farm_phrase(m.group("location") or "")
    return name, location


def _match_delete_farm(text: str) -> str | None:
    m = _DELETE_FARM_RE.match(text.strip())
    if not m:
        return None
    name = _clean_farm_phrase(m.group("name"))
    return name or None


def _match_rename_farm(text: str) -> tuple[str, str] | None:
    m = _RENAME_FARM_RE.match(text.strip())
    if not m:
        return None
    old = _clean_farm_phrase(m.group("old"))
    new = _clean_farm_phrase(m.group("new"))
    if not old or not new:
        return None
    return old, new


def _match_relocate_farm(text: str) -> tuple[str, str] | None:
    stripped = text.strip()
    m = _RELOCATE_FARM_RE_A.match(stripped) or _RELOCATE_FARM_RE_B.match(stripped)
    if not m:
        return None
    name = _clean_farm_phrase(m.group("name") or "")
    location = _clean_farm_phrase(m.group("location"))
    if not location:
        return None
    return name, location


def _match_relocate_no_dest(text: str) -> str | None:
    """("update my farm's location") -> "" (generic filler, resolved to
    the active farm by _resolve_farm_reference); ("change the location of
    North Field") -> "North Field". Returns None if the message doesn't
    match this shape at all (including when it HAS a destination -- callers
    check _match_relocate_farm first)."""
    m = _RELOCATE_NO_DEST_RE.match(text.strip())
    if not m:
        return None
    name = _clean_farm_phrase(m.group("name1") or m.group("name2") or "")
    if name.lower() in _GENERIC_FARM_REF:
        name = ""
    return name


_LEADING_TRAILING_FARM_RE = re.compile(r"^farm\s+|\s+farm$", re.IGNORECASE)


def _resolve_farm_reference(session: SessionState, name: str) -> int | None:
    """A farm named in a management command ("delete Farm 2") -- exact
    name match on the phrase AS SAID first (so a farm genuinely named
    "Farm 1" -- the app's own auto-generated default -- still matches),
    then the same loose in-sentence match voice answers to the ambiguous-
    farm question use, then a leading/trailing "farm" stripped as a generic
    noun (for "delete the north field farm" when the real name is "North
    Field"), then (only for an empty/missing name, e.g. "delete this
    farm") this session's own already-resolved farm. Never guesses across
    multiple equally-plausible matches."""
    if name:
        idx = _find_farm_by_name(name)
        if idx is not None:
            return idx
        idx = _find_farm_in_speech(name)
        if idx is not None:
            return idx
        stripped = _clean_farm_phrase(_LEADING_TRAILING_FARM_RE.sub("", name))
        if stripped and stripped != name:
            idx = _find_farm_by_name(stripped)
            if idx is not None:
                return idx
            return _find_farm_in_speech(stripped)
        return None
    return session.active_farm_index


def _add_farm_reply(name: str, location: str, text: str, session: SessionState) -> dict:
    """Shared by the add-farm regex and interpret()'s add_farm action."""
    explicit_name = bool(name)
    name = name or _unique_default_name()
    # Only prompt when the farmer actually SAID this name -- an
    # auto-generated default is picked collision-free by
    # _unique_default_name() already, so there's nothing to ask about.
    if explicit_name and _name_collides(name):
        session.pending_new_farm_name = (location,)
        existing = ", ".join(f.name for f in _farm_state.farms)
        return _reply(
            "general",
            f"You already have a farm called {name}. What would you like to name this new one? "
            f"(Existing: {existing}.)",
            None,
            text,
            session.session_id,
        )
    idx = _farm_state.add_farm(name, location=location, location_confirmed=bool(location))
    session.active_farm_index = idx
    _farm_store.save(config.FARM_STATE_PATH)
    if location:
        response = f"Added {name}, set to {location}."
    else:
        # Without this pending marker the farmer's next reply (the place
        # name) was routed as a weather question and answered with a
        # forecast instead of being saved to the new farm.
        session.pending_new_farm_location = idx
        response = f"Added {name}. What town or area is it in?"
    return _reply("general", response, _farm_state.farms[idx], text, session.session_id)


def _select_farm_reply(idx: int, text: str, session: SessionState) -> dict:
    session.active_farm_index = idx
    _farm_state.set_active(idx)
    _farm_store.save(config.FARM_STATE_PATH)
    farm = _farm_state.farms[idx]
    where = f" in {farm.location}" if farm.location else ""
    return _reply("general", f"Okay, we're on {farm.name}{where} now. What would you like to know?", farm, text, session.session_id)


def _handle_farm_management(text: str, session: SessionState, mid_plant: bool = False) -> dict | None:
    """Deterministic add/rename/relocate/delete/list commands -- returns a
    reply dict if `text` matched one, else None (falls through to normal
    domain routing). Checked before the pending-location/farewell/domain
    logic in _answer() since these commands are about the farm list, not a
    question for any domain agent."""
    stripped = text.strip()

    # A pending deletion confirmation always takes priority (a yes/no reply
    # shouldn't be re-interpreted as a "list my farms" question just
    # because it happens to contain the word "farm").
    if session.pending_farm_deletion is not None:
        idx, name = session.pending_farm_deletion
        if _CONFIRM_YES_RE.match(stripped):
            session.pending_farm_deletion = None
            if 0 <= idx < len(_farm_state.farms) and _farm_state.farms[idx].name == name:
                _delete_farm(idx)
                return _reply("general", f"Deleted {name}.", None, text, session.session_id)
            return _reply("general", f"{name} is already gone.", None, text, session.session_id)
        if _CONFIRM_NO_RE.match(stripped):
            session.pending_farm_deletion = None
            return _reply("general", "Okay, keeping it.", None, text, session.session_id)
        return _reply(
            "general",
            f"Sorry, just say yes or no -- delete {name}?",
            None,
            text,
            session.session_id,
        )

    if _LIST_FARMS_RE.search(stripped):
        if not _farm_state.farms:
            response = "You don't have any farms yet. Say \"add a farm\" to create one."
        elif len(_farm_state.farms) == 1:
            f = _farm_state.farms[0]
            response = f"You have one farm: {f.name}" + (f", in {f.location}." if f.location else ", no location set yet.")
        else:
            parts = [f"{f.name} ({f.location})" if f.location else f"{f.name} (no location set)" for f in _farm_state.farms]
            response = f"You have {len(_farm_state.farms)} farms: " + ", ".join(parts) + "."
        return _reply("general", response, None, text, session.session_id)

    add_match = _match_add_farm(stripped)
    if add_match is not None:
        return _add_farm_reply(*add_match, text, session)

    delete_name = _match_delete_farm(stripped)
    if delete_name is not None:
        idx = _resolve_farm_reference(session, delete_name)
        if idx is None or not (0 <= idx < len(_farm_state.farms)):
            names = ", ".join(f.name for f in _farm_state.farms) or "none yet"
            return _reply(
                "general",
                f"I couldn't find a farm called {delete_name or 'that'}. Your farms are: {names}.",
                None,
                text,
                session.session_id,
            )
        farm = _farm_state.farms[idx]
        session.pending_farm_deletion = (idx, farm.name)
        return _reply(
            "general",
            f"Delete {farm.name}? This removes all its history and can't be undone -- say yes to confirm.",
            None,
            text,
            session.session_id,
        )

    rename_match = _match_rename_farm(stripped)
    if rename_match is not None:
        old, new = rename_match
        idx = _resolve_farm_reference(session, old)
        if idx is None or not (0 <= idx < len(_farm_state.farms)):
            names = ", ".join(f.name for f in _farm_state.farms) or "none yet"
            return _reply(
                "general", f"I couldn't find a farm called {old}. Your farms are: {names}.", None, text, session.session_id
            )
        # Farm names are kept unique (2026-09-28, explicit user choice:
        # "when renaming ... if it is the same name, prompt to change it
        # to be unique"). exclude_idx=idx so renaming a farm to its own
        # current name is a harmless no-op, not flagged as a collision.
        if _name_collides(new, exclude_idx=idx):
            session.pending_rename = (idx, _farm_state.farms[idx].name)
            existing = ", ".join(f.name for f in _farm_state.farms)
            return _reply(
                "general",
                f"You already have a farm called {new}. What would you like to rename "
                f"{_farm_state.farms[idx].name} to instead? (Existing: {existing}.)",
                None,
                text,
                session.session_id,
            )
        _farm_state.farms[idx].name = new
        _farm_store.save(config.FARM_STATE_PATH)
        return _reply("general", f"Renamed {old} to {new}.", _farm_state.farms[idx], text, session.session_id)

    relocate_match = _match_relocate_farm(stripped)
    if relocate_match is not None:
        name, location = relocate_match
        idx = _resolve_farm_reference(session, name)
        if idx is None or not (0 <= idx < len(_farm_state.farms)):
            names = ", ".join(f.name for f in _farm_state.farms) or "none yet"
            return _reply(
                "general",
                f"I couldn't find a farm called {name or 'that'}. Your farms are: {names}.",
                None,
                text,
                session.session_id,
            )
        farm = _farm_state.farms[idx]
        farm.location = location
        farm.location_confirmed = True
        farm.country_code = ""  # stale until the next weather call re-geocodes
        _farm_store.save(config.FARM_STATE_PATH)
        return _reply("general", f"{farm.name} is now set to {location}.", farm, text, session.session_id)

    # No destination given yet ("update my farm's location") -- ask for
    # one and remember which farm via pending_relocate_farm, same pattern
    # as pending_new_farm_location. See that field's docstring for the
    # LLM-hallucinated-success bug this fixes.
    relocate_name = _match_relocate_no_dest(stripped)
    if relocate_name is not None:
        idx = _resolve_farm_reference(session, relocate_name)
        if idx is None or not (0 <= idx < len(_farm_state.farms)):
            names = ", ".join(f.name for f in _farm_state.farms) or "none yet"
            return _reply(
                "general",
                f"I couldn't find a farm called {relocate_name or 'that'}. Your farms are: {names}.",
                None,
                text,
                session.session_id,
            )
        farm = _farm_state.farms[idx]
        session.pending_relocate_farm = idx
        return _reply(
            "general",
            f"Sure -- what town or area should I set {farm.name}'s location to?",
            farm,
            text,
            session.session_id,
        )

    # REAL BUG FOUND AND FIXED (2026-09-27, reported live: said "delete"
    # then, separately, just "farm 1" -- got "sorry, I didn't catch that"
    # instead of "what should I do with Farm 1?"). Every command above
    # requires the verb and the farm name in the SAME message; a farm name
    # said on its own, with no command and nothing else pending, used to
    # match nothing at all and fall through to the generic domain router
    # (which also has no keyword for a bare "farm 1"). Only fires when the
    # message is basically JUST a farm name (nothing else going on) so an
    # ordinary sentence that happens to mention a farm ("how's farm 1
    # doing") isn't hijacked into this.
    if not mid_plant and len(stripped.split()) <= 4:
        idx = _find_farm_by_name(stripped)
        if idx is not None:
            farm = _farm_state.farms[idx]
            return _reply(
                "general",
                f"What would you like to do with {farm.name} -- delete it, rename it, "
                "change its location, or make it active?",
                farm,
                text,
                session.session_id,
            )

    return None


def _reply(domain: str, response: str, farm: FarmProfile | None, text: str, session_id: str, **extra) -> dict:
    session = _sessions.get(session_id)
    if session is not None:
        session.history.extend([("farmer", text), ("assistant", response)])
        del session.history[:-20]
    # Farmer-scoped, not farm-scoped -- see TranscriptEntry's docstring.
    # Recorded even when `farm` is None (farm management, farewells, mic
    # checks) so the visible chat log can be replayed in full on a page
    # refresh via GET /conversation, not just the subset that happened to
    # have a farm attached.
    if text.strip():
        _farm_state.add_transcript_entry("you", domain, text)
    _farm_state.add_transcript_entry("agent", domain, response)
    if farm is not None:
        farm.add_chat_turn(domain=domain, role="farmer", text=text)
        farm.add_chat_turn(domain=domain, role="agent", text=response)
    _farm_store.save(config.FARM_STATE_PATH)
    done = _domain_conversation_done(domain, session_id) if domain in MULTI_TURN_DOMAINS else True
    return {"domain": domain, "response": response, "done": done, "farm_state": _farm_state.to_dict(), **extra}


def _answer(
    text: str,
    location: str | None = None,
    farm_name: str | None = None,
    crop: str | None = None,
    session_id: str | None = None,
    farmer_id: str | None = None,
) -> dict:
    """Shared by typed /chat and the /voice WebSocket, so both behave the
    same: clarify instead of guessing, ask for a location before answering
    weather when none is known, and hand every agent the actual question."""
    _use_farm_state(farmer_id)
    session = _get_session(session_id)

    text = (text or "").strip()
    if not text:
        return _reply("general", CLARIFY_TEXT, None, text, session.session_id)

    # A farewell ends the conversation outright and clears any pending
    # question -- checked FIRST and unconditionally except mid multi-turn
    # Plant diagnosis (a short answer like "that's it" could coincidentally
    # match a real follow-up answer there). REAL BUG FOUND AND FIXED
    # (2026-09-27, reported live: "thank you" kept getting answered with
    # 'Sorry, I couldn't find that place'): this used to skip the farewell
    # check whenever a location or farm question was pending, so "thank
    # you" fell through to the pending-location branch below, which had
    # nothing better to do than treat "thank you" itself as the place name,
    # fail to geocode it, and ask again. _is_farewell() only matches whole
    # phrases (not substrings), so it's always safe to check first.
    mid_plant_conversation = session.current_domain == "plant" and not _domain_conversation_done("plant", session.session_id)
    if not mid_plant_conversation and _is_farewell(text):
        session.pending_location_question = None
        session.pending_farm_question = None
        session.pending_farm_deletion = None
        session.pending_new_farm_location = None
        session.pending_new_farm_name = None
        session.pending_rename = None
        session.pending_relocate_farm = None
        farm = _farm_state.farms[session.active_farm_index] if session.active_farm_index is not None else None
        return _reply("general", GOODBYE_TEXT, farm, text, session.session_id, end_conversation=True)

    # A mic check, not a real question -- deliberately does NOT clear any
    # pending_* state (unlike farewell above): "can you hear me" asked
    # mid-way through answering a real pending question shouldn't reset
    # that progress, just answer the mic check and leave the pending
    # question to be answered next turn.
    if _is_mic_check(text):
        farm = _farm_state.farms[session.active_farm_index] if session.active_farm_index is not None else None
        return _reply("general", MIC_CHECK_TEXT, farm, text, session.session_id)

    # The farmer is answering "what town or area is it in?" for a farm they
    # JUST created -- takes priority over everything below (including farm
    # management commands: a struggling/hesitant reply here shouldn't
    # accidentally parse as some other command) so the location is applied
    # directly to that farm, never forwarded to a weather agent as if it
    # were an ordinary "where's my farm" answer. See pending_new_farm_location's
    # docstring for the bug this fixes.
    if not mid_plant_conversation and session.pending_new_farm_location is not None:
        idx = session.pending_new_farm_location
        if not (0 <= idx < len(_farm_state.farms)):
            # The farm was deleted from under this pending question (e.g.
            # from another tab) -- don't keep asking about something that
            # no longer exists.
            session.pending_new_farm_location = None
        else:
            # REAL BUG FOUND AND FIXED (2026-09-29, live screenshot: "In
            # Colombo." and "The second farm location is Jaffna." both got
            # "sorry, I didn't catch a place name there"). This used
            # _clean_farm_phrase() -- punctuation-only stripping -- so the
            # lead-in words ("In ", "The second farm location is ") were
            # sent to the geocoder as part of the place name and failed to
            # resolve. Swapped to _location_from_reply(), the same
            # lead-in-stripping helper the ordinary pending-weather/crop-
            # location flow already uses correctly (see
            # pending_location_question above).
            place = _location_from_reply(text)
            farm = _farm_state.farms[idx]
            # Geocode it for real rather than guessing from word shape --
            # REAL BUG FOUND AND FIXED (2026-09-27): a word-list heuristic
            # here accepted "umm let me think" as a place name outright
            # (none of its words happened to be on the blocklist). The
            # weather agent's own geocoder is the actual source of truth
            # for "is this a real place", the same one every other location
            # in this app is validated against.
            weather_agent = _agents.get("weather")
            geocode_failed = False
            if place and weather_agent is not None:
                try:
                    _, _, country_code = weather_agent.geocode(place)
                except ValueError:
                    geocode_failed = True
                except Exception:  # noqa: BLE001 -- network/API hiccup: don't block farm creation over it
                    country_code = ""
                else:
                    session.pending_new_farm_location = None
                    farm.location = place
                    farm.location_confirmed = True
                    farm.country_code = country_code
                    _farm_store.save(config.FARM_STATE_PATH)
                    return _reply("general", f"{farm.name} is set to {place}.", farm, text, session.session_id)
            if place and not geocode_failed and weather_agent is None:
                # No weather agent configured (missing API key) -- can't
                # verify, so accept it as given rather than blocking farm
                # setup entirely on an unrelated missing key.
                session.pending_new_farm_location = None
                farm.location = place
                farm.location_confirmed = True
                _farm_store.save(config.FARM_STATE_PATH)
                return _reply("general", f"{farm.name} is set to {place}.", farm, text, session.session_id)
            return _reply(
                "general",
                "Sorry, I didn't catch a place name there. What town or area is your farm in?",
                farm,
                text,
                session.session_id,
            )

    # The farmer is answering "what town or area should I set FARM's
    # location to?" from the no-destination relocate flow above -- same
    # geocode-validate-then-apply shape as pending_new_farm_location just
    # above (deliberately duplicated rather than shared: the two success/
    # failure messages differ and the fields being cleared differ, and this
    # block is short enough that a shared helper would just move the
    # reading, not simplify it). See pending_relocate_farm's docstring on
    # SessionState for the bug this fixes.
    if not mid_plant_conversation and session.pending_relocate_farm is not None:
        idx = session.pending_relocate_farm
        if not (0 <= idx < len(_farm_state.farms)):
            session.pending_relocate_farm = None
        else:
            place = _location_from_reply(text)
            farm = _farm_state.farms[idx]
            weather_agent = _agents.get("weather")
            geocode_failed = False
            if place and weather_agent is not None:
                try:
                    _, _, country_code = weather_agent.geocode(place)
                except ValueError:
                    geocode_failed = True
                except Exception:  # noqa: BLE001 -- network/API hiccup: don't block the update over it
                    country_code = ""
                else:
                    session.pending_relocate_farm = None
                    farm.location = place
                    farm.location_confirmed = True
                    farm.country_code = country_code
                    _farm_store.save(config.FARM_STATE_PATH)
                    return _reply("general", f"{farm.name} is now set to {place}.", farm, text, session.session_id)
            if place and not geocode_failed and weather_agent is None:
                session.pending_relocate_farm = None
                farm.location = place
                farm.location_confirmed = True
                _farm_store.save(config.FARM_STATE_PATH)
                return _reply("general", f"{farm.name} is now set to {place}.", farm, text, session.session_id)
            return _reply(
                "general",
                "Sorry, I didn't catch a place name there. What town or area should I set it to?",
                farm,
                text,
                session.session_id,
            )

    # The farmer is giving a unique name after "you already have a farm
    # called X" -- see _add_farm_reply(). Re-prompts (keeps this pending)
    # if the new name ALSO collides, rather than silently creating a
    # duplicate or guessing.
    if not mid_plant_conversation and session.pending_new_farm_name is not None:
        (location,) = session.pending_new_farm_name
        candidate = _clean_farm_phrase(text)
        if not candidate:
            return _reply(
                "general", "Sorry, what would you like to name it?", None, text, session.session_id
            )
        if _name_collides(candidate):
            existing = ", ".join(f.name for f in _farm_state.farms)
            return _reply(
                "general",
                f"You already have a farm called {candidate} too. Try a different name? (Existing: {existing}.)",
                None,
                text,
                session.session_id,
            )
        session.pending_new_farm_name = None
        return _add_farm_reply(candidate, location, text, session)

    # The farmer is giving a unique replacement name after "you already
    # have a farm called X" during a rename -- see the rename branch in
    # _handle_farm_management(). Same re-prompt-on-collision behavior.
    if not mid_plant_conversation and session.pending_rename is not None:
        idx, old_name = session.pending_rename
        if not (0 <= idx < len(_farm_state.farms)) or _farm_state.farms[idx].name != old_name:
            # The farm was deleted or already renamed from under this
            # pending question (e.g. from another tab) -- don't keep
            # asking about something that no longer matches.
            session.pending_rename = None
        else:
            candidate = _clean_farm_phrase(text)
            if not candidate:
                return _reply(
                    "general", f"Sorry, what would you like to rename {old_name} to?", None, text, session.session_id
                )
            if _name_collides(candidate, exclude_idx=idx):
                existing = ", ".join(f.name for f in _farm_state.farms)
                return _reply(
                    "general",
                    f"You already have a farm called {candidate} too. Try a different name? (Existing: {existing}.)",
                    None,
                    text,
                    session.session_id,
                )
            session.pending_rename = None
            _farm_state.farms[idx].name = candidate
            _farm_store.save(config.FARM_STATE_PATH)
            return _reply(
                "general", f"Renamed {old_name} to {candidate}.", _farm_state.farms[idx], text, session.session_id
            )

    # Farm management (add/rename/relocate/delete/list farms) -- checked
    # before domain routing and the pending-location/pending-farm-choice
    # branches, since these commands are about the farm LIST, not a
    # question for any domain agent. Also handles a pending "delete FARM?
    # yes/no" reply.
    # Checked even mid plant diagnosis: that lock used to swallow "add a
    # farm" and every other command as a symptom answer until the
    # diagnosis finished. These regexes need an explicit command verb, so a
    # real symptom answer won't match them (the bare-farm-name fallback,
    # which could, is skipped via mid_plant).
    managed = _handle_farm_management(text, session, mid_plant=mid_plant_conversation)
    if managed is not None:
        if mid_plant_conversation:
            _agents["plant"].abandon(session.session_id)
            session.current_domain = "general"
        return managed

    # The farmer is answering our "which farm is this about?" question --
    # by voice or typed text, not just by tapping the picker (which instead
    # resends the ORIGINAL question with farm_name set, bypassing this).
    if session.pending_farm_question is not None:
        idx = _find_farm_by_name(text) if farm_name is None else _find_farm_by_name(farm_name)
        if idx is None:
            idx = _find_farm_in_speech(text)
        if idx is not None:
            pending_domain, pending_text = session.pending_farm_question
            session.pending_farm_question = None
            session.active_farm_index = idx
            _farm_state.set_active(idx)
            farm = _farm_state.farms[idx]
            agent = _agents.get(pending_domain)
            try:
                if pending_domain in MULTI_TURN_DOMAINS:
                    response = agent.handle(farm, pending_text, crop=crop, session_id=session.session_id)
                elif pending_domain == "weather":
                    response = agent.handle(farm, location=location, question=pending_text)
                else:
                    response = agent.handle(farm, crop_name=crop, question=pending_text)
            except Exception as exc:  # noqa: BLE001
                response = f"Something went wrong handling that: {exc}"
            return _reply(pending_domain, response, farm, pending_text, session.session_id)
        # Didn't recognise a farm name in that reply -- ask again rather
        # than silently guessing or falling through to normal routing
        # (which would treat "the north one" as an unrelated new question).
        names = ", ".join(f.name for f in _farm_state.farms)
        return _reply(
            "general",
            f"Sorry, I didn't catch which farm. It's one of: {names}?",
            None,
            text,
            session.session_id,
        )

    # The farmer is answering our "which town is your farm in?" question --
    # unless they've clearly moved on to a different domain's question
    # instead, or the reply plainly isn't a place at all (see
    # _looks_like_a_place's docstring for the bug this guards against: this
    # branch used to accept ANY non-crop/plant text as the location and
    # geocode it literally, so a garbled or off-topic reply -- reported live
    # on mobile, where ASR transcripts are noisier -- got sent to the
    # weather API as a place name and just failed, re-asking forever).
    # Originally weather-only; now shared with crop, since crop suitability
    # reads farm climate/country too -- see pending_location_question's
    # docstring for the "answered a generic crop list instead of asking for
    # location" bug this fixes.
    if session.pending_location_question is not None:
        pending_domain, pending = session.pending_location_question
        other_domains = {"crop", "plant", "weather"} - {pending_domain}
        if detect_domain(text) not in other_domains:
            place = location or _location_from_reply(text)
            if location or _looks_like_a_place(text, place):
                farm, _, _ = resolve_active_farm(session, farm_name, place)
                pending_agent = _agents.get(pending_domain)
                try:
                    if pending_domain == "weather":
                        response = pending_agent.handle(farm, location=place, question=pending)
                    else:
                        farm.location = place
                        farm.location_confirmed = True
                        response = pending_agent.handle(farm, crop_name=crop, question=pending)
                except ValueError:
                    return _reply(pending_domain, LOCATION_NOT_FOUND_TEXT, farm, text, session.session_id)
                except Exception as exc:  # noqa: BLE001
                    response = f"Something went wrong handling that: {exc}"
                session.pending_location_question = None
                return _reply(pending_domain, response, farm, text, session.session_id)
            # Doesn't look like a place -- ask again rather than guessing,
            # but don't just silently drop whatever they actually said either.
            farm = _farm_state.farms[session.active_farm_index] if session.active_farm_index is not None else None
            return _reply(
                pending_domain,
                "Sorry, I didn't catch a place name there. Which town or city is your farm near?",
                farm,
                text,
                session.session_id,
            )
    session.pending_location_question = None

    domain, is_fresh_exchange, switched = route_message(text, session)
    if domain is None:
        # No keyword matched. This used to be a hard "Sorry, I didn't catch
        # that" -- reported live for "let's focus on the farm in Zurich" and
        # context-dependent follow-ups. interpret() reads the conversation
        # and farm list and decides what was meant.
        try:
            result = interpret(
                text,
                session.history,
                [(f.name, f.location) for f in _farm_state.farms],
                _farm_state.farms[session.active_farm_index].name if session.active_farm_index is not None else None,
            )
        except RuntimeError:
            return _reply("general", CLARIFY_TEXT, None, text, session.session_id)
        action = result.get("action")
        if action == "select_farm":
            idx = _find_farm_by_name(str(result.get("farm") or ""))
            if idx is not None:
                return _select_farm_reply(idx, text, session)
            names = ", ".join(f"{f.name} ({f.location})" if f.location else f.name for f in _farm_state.farms)
            return _reply("general", f"Which farm do you mean? You have: {names or 'no farms yet'}.", None, text, session.session_id)
        if action == "add_farm":
            name = _clean_farm_phrase(str(result.get("name") or ""))
            new_location = _clean_farm_phrase(str(result.get("location") or ""))
            # The model sometimes fills in a name the farmer never gave
            # ("Galle" for "a new farm in Galle", or "New Farm").
            if name.lower() in (new_location.lower(), "new farm", "farm", "another farm"):
                name = ""
            return _add_farm_reply(name, new_location, text, session)
        if action in ("answer", "unclear"):
            reply = str(result.get("reply") or "").strip() or CLARIFY_TEXT
            return _reply("general", reply, None, text, session.session_id)
        domain = action
        if result.get("question"):
            text = str(result["question"])
        if result.get("farm"):
            farm_name = str(result["farm"])
        is_fresh_exchange = True
        switched = domain != session.current_domain
        session.current_domain = domain

    agent = _agents.get(domain)
    if agent is None:
        return _reply(domain, f"The {domain} assistant isn't available right now.", None, text, session.session_id)

    if is_fresh_exchange:
        # "what's the weather at the Zurich farm" -- a farm named in the
        # sentence itself shouldn't trigger the "which farm?" question.
        if farm_name is None and len(_farm_state.farms) > 1:
            idx = _find_farm_in_speech(text)
            if idx is not None:
                farm_name = _farm_state.farms[idx].name
        # "weather at Alpine tomorrow", where Alpine is the farm's NAME: the
        # weather agent reads "at <Capitalized>" as a one-off place, and
        # "Alpine" geocoded to a town in Texas (seen live: Texas weather
        # reported for a farm in Zurich). Swap a farm name for its location.
        named = extract_location(text)
        idx = _find_farm_by_name(named) if named else None
        if idx is not None:
            farm_name = farm_name or _farm_state.farms[idx].name
            text = text.replace(named, _farm_state.farms[idx].location or "my farm")
        farm, _, ambiguous = resolve_active_farm(session, farm_name, location)
        if ambiguous is not None:
            # Held so the farmer's NEXT reply (by voice or text, not just a
            # picker tap) answers this instead of being routed as a new,
            # unrelated question -- see the pending_farm_question check above.
            session.pending_farm_question = (domain, text)
            response = "You have more than one farm -- which one is this about: " + ", ".join(ambiguous) + "?"
            return _reply(domain, response, None, text, session.session_id, ambiguous_farms=ambiguous)
    else:
        # Mid multi-turn Plant diagnosis: keep the farm it started on.
        farm, _, _ = resolve_active_farm(session, None, None)

    # Both weather and crop answers depend on the farm's actual climate/
    # location (farm.to_prompt_context() feeds it into both) -- REAL BUG
    # FOUND AND FIXED (2026-09-27, reported live: "what should I grow" with
    # no location set just answered a generic crop list instead of asking):
    # this gate used to be weather-only, so a location-less crop question
    # skipped straight to an answer, and if the farmer then volunteered a
    # location afterward, pending_location_question (then weather-only
    # too) had nothing to anchor it to and it fell through to "didn't
    # catch that" instead of being applied.
    if domain in ("weather", "crop") and not location and not farm.location_confirmed and not extract_location(text):
        session.pending_location_question = (domain, text)
        return _reply(domain, ASK_LOCATION_TEXT, farm, text, session.session_id, switched=switched)

    try:
        if domain in MULTI_TURN_DOMAINS:
            response = agent.handle(farm, text, crop=crop, session_id=session.session_id)
        elif domain == "weather":
            response = agent.handle(farm, location=location, question=text)
        else:
            response = agent.handle(farm, crop_name=crop, question=text)
    except Exception as exc:  # noqa: BLE001 -- surface the failure to the farmer, don't crash the server
        response = f"Something went wrong handling that: {exc}"

    return _reply(domain, response, farm, text, session.session_id, switched=switched)


@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn) -> ChatOut:
    """Typed-text path -- see _answer(). Runs in a worker thread because
    the agents make blocking HTTP/LLM calls."""
    result = await asyncio.to_thread(
        _answer, body.text, body.location, body.farm_name, body.crop, body.session_id, body.farmer_id
    )
    return ChatOut(**result)


@app.websocket("/voice")
async def voice_session(websocket: WebSocket, session_id: str | None = None, farmer_id: str | None = None) -> None:
    """Real-microphone path: browser streams raw 16-bit PCM audio frames
    over this socket, server feeds them to StreamingASR, and the final
    transcript is routed the same way as a typed /chat message once ASR
    reports end-of-turn -- see module docstring. UNVERIFIED end-to-end, no
    AssemblyAI key configured in this project yet. `session_id` (a query
    param, e.g. /voice?session_id=...) scopes farm/domain/diagnosis state
    to this browser tab -- see SessionState. `farmer_id` (same query-param
    style) scopes which farms exist at all -- see FarmStore/_use_farm_state().
    """
    await websocket.accept()

    if not config.ASSEMBLYAI_API_KEY:
        await websocket.send_json({"type": "error", "message": "Voice input needs ASSEMBLYAI_API_KEY to be set."})
        await websocket.close()
        return

    loop = asyncio.get_running_loop()

    def on_final_transcript(transcript: str) -> None:
        asyncio.run_coroutine_threadsafe(
            _handle_voice_transcript(websocket, transcript, session_id, farmer_id), loop
        )

    try:
        asr = StreamingASR(on_final_transcript=on_final_transcript)
        # StreamingASR.connect() is a BLOCKING call -- it only returns once
        # AssemblyAI's websocket handshake actually succeeds, which includes
        # an internal SDK retry after an initial SSL handshake timeout
        # (~4.6-4.8s observed on this machine, reproducible every time, see
        # docs/build_log.md). Run it in a thread so this coroutine doesn't
        # block the event loop, and explicitly signal "ready" to the browser
        # only once it returns -- the browser must not start streaming PCM
        # before this, or the first several seconds of the farmer's speech
        # never reach AssemblyAI (this was the root cause of transcripts
        # like "what is the weather" coming back as garbled fragments).
        await loop.run_in_executor(None, asr.connect)
    except Exception as exc:  # noqa: BLE001 -- report connection failure, don't crash the endpoint
        await websocket.send_json({"type": "error", "message": f"Could not start voice session: {exc}"})
        await websocket.close()
        return

    await websocket.send_json({"type": "ready"})

    try:
        while True:
            data = await websocket.receive_bytes()
            asr.send_audio(data)
    except WebSocketDisconnect:
        pass
    finally:
        asr.disconnect()


async def _handle_voice_transcript(
    websocket: WebSocket, transcript: str, session_id: str | None, farmer_id: str | None = None
) -> None:
    # REAL FEATURE ADDED (2026-09-28, user asked for a distinct "thinking"
    # indicator, separate from "listening" and "answering"). Before this,
    # the client had no way to know ASR had already finalized the
    # transcript -- "result" below is the FIRST message sent after
    # end-of-turn, and it only arrives once _answer() (routing, weather/
    # Gemini calls, everything) has ALSO finished, so the farmer saw
    # nothing change for however long that took (measured up to ~20s for
    # an interpreter-routed message, see docs/USER_GUIDE.md's latency
    # table) -- dead air with no feedback that anything was happening.
    # Sending the transcript the moment ASR is done, before _answer()
    # even starts, lets the client switch to a "thinking" state
    # immediately (and show what was actually heard, while the real
    # answer is still being computed) instead of the "listening" state
    # just going stale until the full reply shows up.
    await websocket.send_json({"type": "transcribed", "transcript": transcript})
    result = await asyncio.to_thread(_answer, transcript, None, None, None, session_id, farmer_id)
    await websocket.send_json({"type": "result", "transcript": transcript, **result})


def main() -> None:
    import argparse
    import os

    import uvicorn

    # Cloud hosts (Render/Railway/Fly.io) inject the port to bind via $PORT
    # and expect the process to listen on 0.0.0.0, not localhost -- local
    # dev still defaults to 127.0.0.1:8001 same as before when $PORT isn't
    # set, so `python -m agri_voice_agent.farmer_server` with no flags
    # keeps working unchanged.
    parser = argparse.ArgumentParser(description="Farmer-facing dashboard server")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8001")))
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
