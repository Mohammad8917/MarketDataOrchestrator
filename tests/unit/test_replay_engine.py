"""FILE: tests/unit/test_replay_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
RESPONSIBILITY: Verify the Backtest replay-engine integration boundary for analytical composition replay.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from backtest.composition_replay import CompositionReplay
from backtest.replay_engine import BacktestReplayEngine
from composition.composer import CompositionRequest
from composition.deterministic_mean import DeterministicEqualWeightMeanComposer


def _request(minute: int, value: float) -> CompositionRequest:
    timestamp = datetime(2026, 10, 1, 9, minute, tzinfo=UTC)
    return CompositionRequest(
        signals={"trend": value, "momentum": value},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"evt-{minute}",
    )


def test_replay_engine_delegates_composition_replay_without_changing_outputs() -> None:
    requests = (_request(0, 0.5), _request(1, -0.25))
    composer = DeterministicEqualWeightMeanComposer()
    engine = BacktestReplayEngine()

    direct = CompositionReplay().run(requests, composer)
    integrated = engine.replay_composition(requests, composer)

    assert integrated == direct


def test_replay_engine_rejects_non_composer() -> None:
    engine = BacktestReplayEngine()

    with pytest.raises(TypeError, match="composer must implement SignalComposer"):
        engine.replay_composition((_request(0, 0.5),), object())  # type: ignore[arg-type]


def test_replay_engine_exposes_composition_replay_contract() -> None:
    engine = BacktestReplayEngine()

    assert engine.composition_replay.contract_id == "backtest_composition_replay_boundary"
    assert engine.composition_replay.contract_version == "1.0.0"
