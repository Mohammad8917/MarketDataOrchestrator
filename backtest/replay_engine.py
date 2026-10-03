"""FILE: backtest/replay_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.7.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Expose the canonical Backtest replay integration boundary for analytical replay consumers.
LAYER: backtest
OWNS: Backtest replay-consumer composition and dependency wiring only.
DOES_NOT_OWN: analytical methodology, market-data I/O, persistence, cost, risk, decision finalization, trading actions
DEPENDENCIES: backtest.composition_replay, backtest.confirmation_replay, backtest.market_structure_replay, backtest.mtf_structure_replay, backtest.setup_replay, composition.composer, composition.confirmation_contract, shared.contracts.equity_curve, shared.contracts.market_structure, shared.contracts.mtf_structure, shared.contracts.performance_metrics, shared.interfaces.setup, shared.interfaces.strategy
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from typing import Any, TypeVar, cast

from backtest.composition_replay import CompositionReplay, CompositionReplayOutput
from backtest.confirmation_replay import ConfirmationReplay, ConfirmationReplayOutput
from backtest.performance_replay import PerformanceAnalysisReplay
from backtest.market_structure_replay import (
    MarketStructureReplay,
    MarketStructureReplayOutput,
)
from backtest.mtf_structure_replay import MtfStructureReplay, MtfStructureReplayOutput
from backtest.setup_replay import SetupReplay, SetupReplayOutput
from backtest.strategy_replay import StrategyReplay, StrategyReplayOutput
from composition.composer import SignalComposer
from composition.confirmation_contract import SignalConfirmation
from shared.contracts.equity_curve import EquityCurve
from shared.contracts.performance_metrics import PerformanceMetricsData
from shared.contracts.market_structure import MarketStructureEvaluator
from shared.contracts.mtf_structure import MtfStructureEvaluator
from shared.interfaces.setup import Setup
from shared.interfaces.strategy import Strategy


TReplay = TypeVar("TReplay")


class BacktestReplayEngine:
    """Wire canonical replay consumers into the Backtest subsystem."""

    def __init__(
        self,
        composition_replay: CompositionReplay | None = None,
        confirmation_replay: ConfirmationReplay | None = None,
        market_structure_replay: MarketStructureReplay | None = None,
        mtf_structure_replay: MtfStructureReplay | None = None,
        setup_replay: SetupReplay | None = None,
        strategy_replay: StrategyReplay | None = None,
        performance_replay: PerformanceAnalysisReplay | None = None,
    ) -> None:
        self.composition_replay = self._require_dependency(
            composition_replay, CompositionReplay, "composition_replay"
        )
        self.confirmation_replay = self._require_dependency(
            confirmation_replay, ConfirmationReplay, "confirmation_replay"
        )
        self.market_structure_replay = self._require_dependency(
            market_structure_replay, MarketStructureReplay, "market_structure_replay"
        )
        self.mtf_structure_replay = self._require_dependency(
            mtf_structure_replay, MtfStructureReplay, "mtf_structure_replay"
        )
        self.setup_replay = self._require_dependency(setup_replay, SetupReplay, "setup_replay")
        self.strategy_replay = self._require_dependency(
            strategy_replay, StrategyReplay, "strategy_replay"
        )
        self.performance_replay = self._require_dependency(
            performance_replay, PerformanceAnalysisReplay, "performance_replay"
        )

    @staticmethod
    def _require_dependency(
        dependency: TReplay | None,
        dependency_type: type[TReplay],
        name: str,
    ) -> TReplay:
        if dependency is None:
            return dependency_type()
        if not isinstance(dependency, dependency_type):
            raise TypeError(f"{name} must implement {dependency_type.__name__}")
        return dependency

    def replay_composition(
        self,
        requests: object,
        composer: SignalComposer,
    ) -> CompositionReplayOutput:
        """Replay composition through the canonical Backtest integration boundary."""
        return self.composition_replay.run(
            cast(Any, requests), composer
        )

    def replay_confirmation(
        self,
        requests: object,
        confirmer: SignalConfirmation,
    ) -> ConfirmationReplayOutput:
        """Replay confirmation through the canonical Backtest integration boundary."""
        return self.confirmation_replay.run(
            cast(Any, requests), confirmer
        )

    def replay_market_structure(
        self,
        requests: object,
        evaluator: MarketStructureEvaluator,
    ) -> MarketStructureReplayOutput:
        """Replay market structure through the canonical Backtest integration boundary."""
        return self.market_structure_replay.run(
            cast(Any, requests), evaluator
        )

    def replay_mtf_structure(
        self,
        requests: object,
        evaluator: MtfStructureEvaluator,
    ) -> MtfStructureReplayOutput:
        """Replay MTF structure through the canonical Backtest integration boundary."""
        return self.mtf_structure_replay.run(
            cast(Any, requests), evaluator
        )

    def replay_setup(
        self,
        requests: object,
        setup: Setup,
    ) -> SetupReplayOutput:
        """Replay setup through the canonical Backtest integration boundary."""
        return self.setup_replay.run(
            cast(Any, requests), setup
        )

    def replay_strategy(
        self,
        requests: object,
        strategy: Strategy,
    ) -> StrategyReplayOutput:
        """Replay strategy evaluation through the canonical Backtest integration boundary."""
        return self.strategy_replay.run(
            cast(Any, requests), strategy
        )

    def calculate_performance_metrics(
        self,
        equity_curve: EquityCurve,
    ) -> PerformanceMetricsData:
        """Calculate terminal performance metrics through the Backtest integration boundary."""
        return self.performance_replay.run(equity_curve).metrics
