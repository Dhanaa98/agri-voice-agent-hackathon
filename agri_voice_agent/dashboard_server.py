"""Local web server hosting the live demo dashboard.

Runs the voice agent's blocking VoiceAgentLoop (mic capture + wakeword +
ASR + domain routing) in a background thread, and serves a single static
HTML page over HTTP plus a WebSocket that broadcasts every AgentEvent the
loop emits (state changes, transcripts, responses, farm_state snapshots).

This lets the dashboard visually prove the project's central claim --
that weather and disease history genuinely shift what the other domains
say -- by showing the shared farm_state updating live alongside the
conversation, rather than only printing to a terminal.

Run with:
    python -m agri_voice_agent.dashboard_server [--domain weather|crop|plant]

Then open http://localhost:8000 in a browser.
"""

from __future__ import annotations

import argparse
import asyncio
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .events import AgentEvent, EventBus
from .main import VoiceAgentLoop

STATIC_DIR = Path(__file__).resolve().parent / "static"

_events = EventBus()
_connections: list[WebSocket] = []
_loop_ref: VoiceAgentLoop | None = None
_main_event_loop: asyncio.AbstractEventLoop | None = None


@asynccontextmanager
async def _lifespan(app: FastAPI):
    global _main_event_loop
    _main_event_loop = asyncio.get_running_loop()
    yield


app = FastAPI(title="Agricultural Voice Agent Dashboard", lifespan=_lifespan)


def _broadcast(event: AgentEvent) -> None:
    """Called from the voice-agent background thread; hands the event to
    the asyncio event loop running the WebSocket connections."""
    if _main_event_loop is None:
        return
    asyncio.run_coroutine_threadsafe(_broadcast_async(event), _main_event_loop)


async def _broadcast_async(event: AgentEvent) -> None:
    dead: list[WebSocket] = []
    for ws in _connections:
        try:
            await ws.send_json(event.to_dict())
        except Exception:  # noqa: BLE001 -- a dropped client shouldn't break the others
            dead.append(ws)
    for ws in dead:
        if ws in _connections:
            _connections.remove(ws)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    _connections.append(websocket)
    if _loop_ref is not None:
        await websocket.send_json(
            {"type": "farm_state", "payload": {"farm_state": _loop_ref.farm_state.to_dict()}, "timestamp": ""}
        )
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in _connections:
            _connections.remove(websocket)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


def _run_voice_agent_loop(forced_domain: str | None) -> None:
    global _loop_ref
    _events.subscribe(_broadcast)
    try:
        _loop_ref = VoiceAgentLoop(forced_domain=forced_domain, events=_events)
        _loop_ref.run()
    except Exception as exc:  # noqa: BLE001 -- keep the dashboard server alive even if the
        # voice loop can't start (e.g. no ASSEMBLYAI_API_KEY yet, no mic present).
        # The page stays up and shows a clear error instead of the background
        # thread silently dying with the browser none the wiser.
        print(f"[dashboard_server] voice agent loop failed to start: {exc}")
        _events.emit("error", domain=None, message=f"Voice agent could not start: {exc}")
        _events.emit("state", status="idle", domain=None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Agricultural voice agent dashboard server")
    parser.add_argument(
        "--domain",
        choices=["weather", "crop", "plant"],
        default=None,
        help="Skip wakeword detection and force one domain active (for demoing before .onnx models exist)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    voice_thread = threading.Thread(
        target=_run_voice_agent_loop, args=(args.domain,), daemon=True, name="voice-agent-loop"
    )
    voice_thread.start()

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
