"""FILE: tests/unit/test_replay_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-10-01
RESPONSIBILITY: Verify the Backtest replay-engine integration boundary for analytical composition and confirmation replay.
LAYER: tests
PYTHON: >=3.13
"""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from backtest.composition_replay import CompositionReplay
from backtest.confirmation_replay import ConfirmationReplay
from backtest.replay_engine import BacktestReplayEngine
from analysis.setup.deterministic_directional_setup import DeterministicDirectionalSetup
from shared.interfaces.setup import SetupRequest
from shared.interfaces.strategy import StrategyOutput, StrategyRequest
from composition.composer import CompositionRequest
from composition.confirmation_contract import ConfirmationRequest
from composition.confirmation.deterministic_threshold import DeterministicThresholdConfirmation
from composition.deterministic_mean import DeterministicEqualWeightMeanComposer
from analysis.structure.market_structure import DeterministicMarketStructureEvaluator
from shared.contracts.market_structure import MarketStructureBar, MarketStructureRequest
from decimal import Decimal


def _timestamp(minute: int) -> datetime:
    return datetime(2026, 10, 1, 9, 0, tzinfo=UTC) + timedelta(minutes=minute)


def _composition_request(minute: int, value: float) -> CompositionRequest:
    timestamp = _timestamp(minute)
    return CompositionRequest(
        signals={"trend": value, "momentum": value},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"evt-{minute}",
    )


def _market_structure_request(minute: int) -> MarketStructureRequest:
    timestamp = _timestamp(minute)
    bar = MarketStructureBar(
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"evt-{minute}",
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("1"),
    )
    bars = tuple(
        replace(
            bar,
            event_time=_timestamp(minute - offset),
            received_at=_timestamp(minute - offset),
            source_event_id=f"evt-{minute}-{offset}",
        )
        for offset in range(4, -1, -1)
    )
    return MarketStructureRequest(bars, timestamp, timestamp, f"evt-{minute}")


def _setup_request(minute: int, value: float) -> SetupRequest:
    timestamp = _timestamp(minute)
    return SetupRequest(
        inputs={"evidence": value},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"evt-{minute}",
    )


class _Strategy:
    contract_id = "test_strategy"
    contract_version = "1.0.0"
    strategy_id = "test"

    def evaluate(self, request: StrategyRequest) -> StrategyOutput:
        return StrategyOutput("hold", 0.5, request.event_time, self.strategy_id)


def _strategy_request(minute: int) -> StrategyRequest:
    timestamp = _timestamp(minute)
    return StrategyRequest(
        inputs={"evidence": 0.5},
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


def test_replay_engine_delegates_setup_replay_without_changing_outputs() -> None:
    requests = (_setup_request(0, 0.8), _setup_request(1, -0.8))
    setup = DeterministicDirectionalSetup()
    engine = BacktestReplayEngine()

    direct = engine.setup_replay.run(requests, setup)
    integrated = engine.replay_setup(requests, setup)

    assert integrated == direct


def test_replay_engine_rejects_non_setup() -> None:
    with pytest.raises(TypeError, match="setup must implement Setup"):
        BacktestReplayEngine().replay_setup((_setup_request(0, 0.5),), object())  # type: ignore[arg-type]


def test_replay_engine_delegates_confirmation_replay_without_changing_outputs() -> None:
    requests = (
        _confirmation_request(0, {"trend": 0.8, "momentum": 0.4}),
        _confirmation_request(1, {"trend": -0.8, "momentum": -0.2}),
    )
    confirmer = DeterministicThresholdConfirmation()
    engine = BacktestReplayEngine()

    direct = ConfirmationReplay().run(requests, confirmer)
    integrated = engine.replay_confirmation(requests, confirmer)

    assert integrated == direct
    assert [item.score for item in integrated.results] == pytest.approx([0.6, -0.5])
    assert [item.confirmed for item in integrated.results] == [True, True]


def test_replay_engine_rejects_non_confirmer() -> None:
    engine = BacktestReplayEngine()

    with pytest.raises(TypeError, match="confirmer must implement SignalConfirmation"):
        engine.replay_confirmation((_confirmation_request(0, {"trend": 0.5}),), object())  # type: ignore[arg-type]


def test_replay_engine_delegates_market_structure_replay_without_changing_outputs() -> None:
    requests = (_market_structure_request(0), _market_structure_request(1))
    evaluator = DeterministicMarketStructureEvaluator()
    engine = BacktestReplayEngine()

    direct = engine.market_structure_replay.run(requests, evaluator)
    integrated = engine.replay_market_structure(requests, evaluator)

    assert integrated == direct


def test_replay_engine_rejects_non_market_structure_evaluator() -> None:
    with pytest.raises(TypeError, match="MarketStructureEvaluator"):
        BacktestReplayEngine().replay_market_structure((_market_structure_request(0),), object())  # type: ignore[arg-type]


def test_replay_engine_exposes_canonical_replay_consumers() -> None:
    engine = BacktestReplayEngine()

    assert engine.composition_replay.contract_id == "backtest_composition_replay_boundary"
    assert engine.composition_replay.contract_version == "1.0.0"
    assert engine.confirmation_replay.contract_id == "backtest_confirmation_replay_boundary"
    assert engine.confirmation_replay.contract_version == "1.0.0"
    assert engine.market_structure_replay.contract_id == "backtest_market_structure_replay_boundary"
    assert engine.market_structure_replay.contract_version == "1.0.0"
    assert engine.setup_replay.contract_id == "backtest_setup_replay_boundary"
    assert engine.setup_replay.contract_version == "1.0.0"
    assert engine.strategy_replay.contract_id == "backtest_strategy_replay_boundary"
    assert engine.strategy_replay.contract_version == "1.0.0"


def test_replay_engine_delegates_strategy_replay_without_changing_outputs() -> None:
    requests = (_strategy_request(0), _strategy_request(1))
    strategy = _Strategy()
    engine = BacktestReplayEngine()

    direct = engine.strategy_replay.run(requests, strategy)
    integrated = engine.replay_strategy(requests, strategy)

    assert integrated == direct


def test_replay_engine_rejects_non_strategy() -> None:
    with pytest.raises(TypeError, match="strategy must implement Strategy"):
        BacktestReplayEngine().replay_strategy((_strategy_request(0),), object())  # type: ignore[arg-type]
