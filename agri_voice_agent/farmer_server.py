"""Farmer-facing dashboard server: one chat, three agents underneath.

Separate from dashboard_server.py (the technical/judge-facing view over
VoiceAgentLoop's continuous mic + wakeword pipeline, which uses its own
"Hey Green"/"Hey Doc" wakewords -- see wakeword/router.py -- and is left
untouched by this file's own single-chat routing).

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
import re
from dataclasses import dataclass
from pathlib import Path

import requests
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .asr import StreamingASR
from .domains.crop import CropAgent
from .domains.plant import PlantAgent
from .domains.weather import WeatherAgent
from .farm_state import FarmProfile, FarmState
from .domains.weather import extract_location
from .intent import classify_with_llm, detect_domain

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
    # The weather question being held while this session waits for a
    # location reply (see _answer()'s pending-location branch).
    pending_weather_question: str | None = None
    # (domain, original question text) being held while this session waits
    # to be told WHICH farm the question is about -- set whenever
    # resolve_active_farm() returns ambiguous_farm_names, answered as soon
    # as the farmer names one, by voice or by tapping the picker (which
    # just resends the original text with farm_name set, bypassing this).
    pending_farm_question: tuple[str, str] | None = None
    # Per-session Plant diagnostic conversation -- PlantAgent's own
    # _active_sessions dict is keyed by whatever session_id we pass it, so
    # this just needs to consistently pass the SAME id for a given browser
    # tab instead of every call defaulting to "default".
    session_id: str = ""


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


_farm_state = FarmState.load(config.FARM_STATE_PATH)
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


def route_message(text: str, session: SessionState, recent_turns: str = "") -> tuple[str | None, bool, bool]:
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
    to plant. Otherwise keywords decide, then the LLM classifier with the
    recent turns as context. There is deliberately no fallback to the
    previously active domain: that used to answer garbled or echoed
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

    detected = detect_domain(text) or classify_with_llm(text, recent_turns)
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
            for name in ("field", "plant")
        },
    }


@app.get("/farm_state")
async def get_farm_state() -> dict:
    return _farm_state.to_dict()


class FarmOut(BaseModel):
    index: int
    name: str
    location: str
    location_confirmed: bool
    active: bool


@app.get("/farms", response_model=list[FarmOut])
async def list_farms() -> list[FarmOut]:
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


@app.post("/farms", response_model=FarmOut)
async def add_farm(body: AddFarmIn) -> FarmOut:
    """Explicitly add a farm from the Farms section UI (as opposed to the
    auto-save-as-"Farm 1" path in resolve_active_farm(), which only fires
    for the very first farm)."""
    name = body.name.strip() or f"Farm {len(_farm_state.farms) + 1}"
    idx = _farm_state.add_farm(name, location=body.location or "", location_confirmed=bool(body.location))
    _farm_state.save(config.FARM_STATE_PATH)
    f = _farm_state.farms[idx]
    return FarmOut(index=idx, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=True)


@app.post("/farms/{index}/select", response_model=FarmOut)
async def select_farm(index: int) -> FarmOut:
    if not (0 <= index < len(_farm_state.farms)):
        raise ValueError(f"No farm at index {index}")
    _farm_state.set_active(index)
    _farm_state.save(config.FARM_STATE_PATH)
    f = _farm_state.farms[index]
    return FarmOut(index=index, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=True)


class UpdateFarmIn(BaseModel):
    name: str | None = None
    location: str | None = None


@app.patch("/farms/{index}", response_model=FarmOut)
async def update_farm(index: int, body: UpdateFarmIn) -> FarmOut:
    """Rename a farm and/or change its saved location after it's already
    been added -- separate from POST /farms (creates a new one) and
    POST /farms/{index}/select (switches which is active). Either field
    may be omitted to leave it unchanged."""
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
    _farm_state.save(config.FARM_STATE_PATH)
    return FarmOut(index=index, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=(index == _farm_state.active_farm_index))


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


_LOCATION_REPLY_PREFIX = re.compile(
    r"^(?:(?:it'?s|it is|my farm is|the farm is|we'?re|we are|i'?m|i am)\s+)?(?:(?:in|at|near|around)\s+)?",
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


def _recent_turns(farm: FarmProfile, n: int = 4) -> str:
    return "\n".join(f"{t.role}: {t.text}" for t in farm.chat_history[-n:])


def _reply(domain: str, response: str, farm: FarmProfile | None, text: str, session_id: str, **extra) -> dict:
    if farm is not None:
        farm.add_chat_turn(domain=domain, role="farmer", text=text)
        farm.add_chat_turn(domain=domain, role="agent", text=response)
        _farm_state.save(config.FARM_STATE_PATH)
    done = _domain_conversation_done(domain, session_id) if domain in MULTI_TURN_DOMAINS else True
    return {"domain": domain, "response": response, "done": done, "farm_state": _farm_state.to_dict(), **extra}


def _answer(
    text: str,
    location: str | None = None,
    farm_name: str | None = None,
    crop: str | None = None,
    session_id: str | None = None,
) -> dict:
    """Shared by typed /chat and the /voice WebSocket, so both behave the
    same: clarify instead of guessing, ask for a location before answering
    weather when none is known, and hand every agent the actual question."""
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
        session.pending_weather_question = None
        session.pending_farm_question = None
        farm = _farm_state.farms[session.active_farm_index] if session.active_farm_index is not None else None
        return _reply("general", GOODBYE_TEXT, farm, text, session.session_id, end_conversation=True)

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
    # unless they've clearly moved on to a crop or plant question instead,
    # or the reply plainly isn't a place at all (see _looks_like_a_place's
    # docstring for the bug this guards against: this branch used to accept
    # ANY non-crop/plant text as the location and geocode it literally, so
    # a garbled or off-topic reply -- reported live on mobile, where ASR
    # transcripts are noisier -- got sent to the weather API as a place
    # name and just failed, re-asking forever).
    if session.pending_weather_question is not None and detect_domain(text) not in ("crop", "plant"):
        pending = session.pending_weather_question
        place = location or _location_from_reply(text)
        if location or _looks_like_a_place(text, place):
            farm, _, _ = resolve_active_farm(session, farm_name, place)
            try:
                response = _agents["weather"].handle(farm, location=place, question=pending)
            except ValueError:
                return _reply("weather", LOCATION_NOT_FOUND_TEXT, farm, text, session.session_id)
            except Exception as exc:  # noqa: BLE001
                response = f"Something went wrong checking the weather: {exc}"
            session.pending_weather_question = None
            return _reply("weather", response, farm, text, session.session_id)
        # Doesn't look like a place -- ask again rather than guessing, but
        # don't just silently drop whatever they actually said either.
        farm = _farm_state.farms[session.active_farm_index] if session.active_farm_index is not None else None
        return _reply(
            "weather",
            "Sorry, I didn't catch a place name there. Which town or city is your farm near?",
            farm,
            text,
            session.session_id,
        )
    session.pending_weather_question = None

    context_farm = (
        _farm_state.farms[session.active_farm_index] if session.active_farm_index is not None else _scratch_farm
    )
    domain, is_fresh_exchange, switched = route_message(text, session, _recent_turns(context_farm))
    if domain is None:
        return _reply("general", CLARIFY_TEXT, context_farm, text, session.session_id)

    agent = _agents.get(domain)
    if agent is None:
        return _reply(domain, f"The {domain} assistant isn't available right now.", None, text, session.session_id)

    if is_fresh_exchange:
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

    if domain == "weather" and not location and not farm.location_confirmed and not extract_location(text):
        session.pending_weather_question = text
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
    result = await asyncio.to_thread(_answer, body.text, body.location, body.farm_name, body.crop, body.session_id)
    return ChatOut(**result)


@app.websocket("/voice")
async def voice_session(websocket: WebSocket, session_id: str | None = None) -> None:
    """Real-microphone path: browser streams raw 16-bit PCM audio frames
    over this socket, server feeds them to StreamingASR, and the final
    transcript is routed the same way as a typed /chat message once ASR
    reports end-of-turn -- see module docstring. UNVERIFIED end-to-end, no
    AssemblyAI key configured in this project yet. `session_id` (a query
    param, e.g. /voice?session_id=...) scopes farm/domain/diagnosis state
    to this browser tab -- see SessionState.
    """
    await websocket.accept()

    if not config.ASSEMBLYAI_API_KEY:
        await websocket.send_json({"type": "error", "message": "Voice input needs ASSEMBLYAI_API_KEY to be set."})
        await websocket.close()
        return

    loop = asyncio.get_running_loop()

    def on_final_transcript(transcript: str) -> None:
        asyncio.run_coroutine_threadsafe(_handle_voice_transcript(websocket, transcript, session_id), loop)

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


async def _handle_voice_transcript(websocket: WebSocket, transcript: str, session_id: str | None) -> None:
    result = await asyncio.to_thread(_answer, transcript, None, None, None, session_id)
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
