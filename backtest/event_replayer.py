"""FILE: backtest/event_replayer.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Implement deterministic historical event replay at its declared backtest subsystem boundary.
LAYER: backtest
OWNS: Only deterministic historical event replay, including source/result type validation and chronological invariants.
DOES_NOT_OWN: live feedback mutation, future data, provider credentials, production side effects
DEPENDENCIES: domain.market_data_event.MarketDataEvent
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from collections.abc import Callable

from domain.market_data_event import MarketDataEvent


class EventReplayer:
    """Replay a deterministic, chronologically ordered historical event stream."""

    def __init__(
        self,
        source: Callable[[], tuple[MarketDataEvent, ...]],
    ) -> None:
        if not callable(source):
            raise TypeError("event source must be callable")
        self._source = source

    def replay(self) -> tuple[MarketDataEvent, ...]:
        """Read, validate, and return the immutable historical event sequence."""
        events = self._source()
        if not isinstance(events, tuple):
            raise TypeError("event source must return a tuple")

        for index, event in enumerate(events):
            if not isinstance(event, MarketDataEvent):
                raise TypeError("event source must contain only MarketDataEvent values")
            if index > 0 and event.event_time <= events[index - 1].event_time:
                raise ValueError("event times must be strictly increasing")

        return events
