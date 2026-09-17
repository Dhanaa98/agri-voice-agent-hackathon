"""Event types broadcast from VoiceAgentLoop to the dashboard server.

Kept separate from main.py so the web server module and any future
consumer (e.g. a TTS layer) can import the event shapes without pulling
in the whole orchestration loop.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Callable, Literal

EventType = Literal[
    "state",  # idle / listening-for-answer, which domain is active
    "transcript",  # a final ASR transcript for the current turn
    "response",  # a domain agent's spoken-style response
    "farm_state",  # a fresh snapshot of the shared FarmState
    "error",
]


@dataclass
class AgentEvent:
    type: EventType
    payload: dict
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


EventListener = Callable[[AgentEvent], None]


class EventBus:
    """Very small synchronous pub/sub -- one process, a handful of listeners."""

    def __init__(self) -> None:
        self._listeners: list[EventListener] = []

    def subscribe(self, listener: EventListener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: EventListener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def emit(self, event_type: EventType, **payload) -> None:
        event = AgentEvent(type=event_type, payload=payload)
        for listener in list(self._listeners):
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 -- a broken UI listener must not kill the voice loop
                print(f"[events] listener error: {exc}")
