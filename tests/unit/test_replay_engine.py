"""FILE: tests/unit/test_replay_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-10-01
RESPONSIBILITY: Verify the Backtest replay-engine integration boundary for analytical composition and confirmation replay.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from backtest.composition_replay import CompositionReplay
from backtest.confirmation_replay import ConfirmationReplay
from backtest.replay_engine import BacktestReplayEngine
from composition.composer import CompositionRequest
from composition.confirmation_contract import ConfirmationRequest
from composition.deterministic_consensus import DeterministicDirectionalConsensus
from composition.deterministic_mean import DeterministicEqualWeightMeanComposer


def _timestamp(minute: int) -> datetime:
    return datetime(2026, 10, 1, 9, minute, tzinfo=UTC)


def _composition_request(minute: int, value: float) -> CompositionRequest:
    timestamp = _timestamp(minute)
    return CompositionRequest(
        signals={"trend": value, "momentum": value},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"evt-{minute}",
    )


def _confirmation_request(minute: int, signals: dict[str, float]) -> ConfirmationRequest:
    timestamp = _timestamp(minute)
    return ConfirmationRequest(
        signals=signals,
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"evt-{minute}",
    )


def test_replay_engine_delegates_composition_replay_without_changing_outputs() -> None:
    requests = (_composition_request(0, 0.5), _composition_request(1, -0.25))
    composer = DeterministicEqualWeightMeanComposer()
    engine = BacktestReplayEngine()

    direct = CompositionReplay().run(requests, composer)
    integrated = engine.replay_composition(requests, composer)

    assert integrated == direct


def test_replay_engine_rejects_non_composer() -> None:
    engine = BacktestReplayEngine()

    with pytest.raises(TypeError, match="composer must implement SignalComposer"):
        engine.replay_composition((_composition_request(0, 0.5),), object())  # type: ignore[arg-type]


def test_replay_engine_delegates_confirmation_replay_without_changing_outputs() -> None:
    requests = (
        _confirmation_request(0, {"trend": 0.8, "momentum": 0.4}),
        _confirmation_request(1, {"trend": -0.8, "momentum": -0.2}),
    )
    confirmer = DeterministicDirectionalConsensus()
    engine = BacktestReplayEngine()

    direct = ConfirmationReplay().run(requests, confirmer)
    integrated = engine.replay_confirmation(requests, confirmer)

    assert integrated == direct


def test_replay_engine_rejects_non_confirmer() -> None:
    engine = BacktestReplayEngine()

    with pytest.raises(TypeError, match="confirmer must implement SignalConfirmation"):
        engine.replay_confirmation((_confirmation_request(0, {"trend": 0.5}),), object())  # type: ignore[arg-type]


def test_replay_engine_exposes_canonical_replay_consumers() -> None:
    engine = BacktestReplayEngine()

    assert engine.composition_replay.contract_id == "backtest_composition_replay_boundary"
    assert engine.composition_replay.contract_version == "1.0.0"
    assert engine.confirmation_replay.contract_id == "backtest_confirmation_replay_boundary"
    assert engine.confirmation_replay.contract_version == "1.0.0"
