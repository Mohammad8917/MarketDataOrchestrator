"""Verify fail-closed dependency wiring for the canonical Backtest replay engine."""

from typing import Any, cast

import pytest

from backtest.composition_replay import CompositionReplay
from backtest.confirmation_replay import ConfirmationReplay
from backtest.market_structure_replay import MarketStructureReplay
from backtest.mtf_structure_replay import MtfStructureReplay
from backtest.performance_replay import PerformanceAnalysisReplay
from backtest.replay_engine import BacktestReplayEngine
from backtest.setup_replay import SetupReplay
from backtest.strategy_replay import StrategyReplay


def test_constructs_canonical_dependencies_by_default() -> None:
    engine = BacktestReplayEngine()

    assert isinstance(engine.composition_replay, CompositionReplay)
    assert isinstance(engine.confirmation_replay, ConfirmationReplay)
    assert isinstance(engine.market_structure_replay, MarketStructureReplay)
    assert isinstance(engine.mtf_structure_replay, MtfStructureReplay)
    assert isinstance(engine.setup_replay, SetupReplay)
    assert isinstance(engine.strategy_replay, StrategyReplay)
    assert isinstance(engine.performance_replay, PerformanceAnalysisReplay)


@pytest.mark.parametrize(
    ("argument", "name", "dependency_type"),
    [
        ("composition_replay", "composition_replay", CompositionReplay),
        ("confirmation_replay", "confirmation_replay", ConfirmationReplay),
        ("market_structure_replay", "market_structure_replay", MarketStructureReplay),
        ("mtf_structure_replay", "mtf_structure_replay", MtfStructureReplay),
        ("setup_replay", "setup_replay", SetupReplay),
        ("strategy_replay", "strategy_replay", StrategyReplay),
        ("performance_replay", "performance_replay", PerformanceAnalysisReplay),
    ],
)
def test_rejects_invalid_dependency(
    argument: str,
    name: str,
    dependency_type: type[object],
) -> None:
    with pytest.raises(TypeError, match=f"{name} must implement {dependency_type.__name__}"):
        BacktestReplayEngine(**cast(Any, {argument: object()}))


@pytest.mark.parametrize(
    ("argument", "dependency_type"),
    [
        ("composition_replay", CompositionReplay),
        ("confirmation_replay", ConfirmationReplay),
        ("market_structure_replay", MarketStructureReplay),
        ("mtf_structure_replay", MtfStructureReplay),
        ("setup_replay", SetupReplay),
        ("strategy_replay", StrategyReplay),
        ("performance_replay", PerformanceAnalysisReplay),
    ],
)
def test_preserves_explicit_dependency_instances(
    argument: str,
    dependency_type: type[object],
) -> None:
    dependency = dependency_type()
    engine = BacktestReplayEngine(**cast(Any, {argument: dependency}))

    assert getattr(engine, argument) is dependency


class FalsyCompositionReplay(CompositionReplay):
    def __bool__(self) -> bool:
        return False


def test_does_not_replace_valid_falsy_dependency() -> None:
    dependency = FalsyCompositionReplay()

    engine = BacktestReplayEngine(composition_replay=dependency)

    assert engine.composition_replay is dependency
