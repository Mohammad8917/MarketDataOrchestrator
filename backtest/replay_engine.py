"""FILE: backtest/replay_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.2.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Expose the canonical Backtest replay integration boundary for analytical replay consumers.
LAYER: backtest
OWNS: Backtest replay-consumer composition and dependency wiring only.
DOES_NOT_OWN: analytical methodology, market-data I/O, persistence, cost, risk, decision finalization, trading actions
DEPENDENCIES: backtest.composition_replay, backtest.confirmation_replay, backtest.market_structure_replay, composition.composer, composition.confirmation_contract, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from backtest.composition_replay import CompositionReplay, CompositionReplayOutput
from backtest.confirmation_replay import ConfirmationReplay, ConfirmationReplayOutput
from backtest.market_structure_replay import (
    MarketStructureReplay,
    MarketStructureReplayOutput,
)
from composition.composer import CompositionRequest, SignalComposer
from composition.confirmation_contract import ConfirmationRequest, SignalConfirmation
from shared.contracts.market_structure import (
    MarketStructureEvaluator,
    MarketStructureRequest,
)


class BacktestReplayEngine:
    """Wire canonical replay consumers into the Backtest subsystem."""

    def __init__(
        self,
        composition_replay: CompositionReplay | None = None,
        confirmation_replay: ConfirmationReplay | None = None,
        market_structure_replay: MarketStructureReplay | None = None,
    ) -> None:
        self.composition_replay = composition_replay or CompositionReplay()
        self.confirmation_replay = confirmation_replay or ConfirmationReplay()
        self.market_structure_replay = (
            market_structure_replay or MarketStructureReplay()
        )

    def replay_composition(
        self,
        requests: tuple[CompositionRequest, ...],
        composer: SignalComposer,
    ) -> CompositionReplayOutput:
        """Replay composition through the canonical Backtest integration boundary."""
        return self.composition_replay.run(requests, composer)

    def replay_confirmation(
        self,
        requests: tuple[ConfirmationRequest, ...],
        confirmer: SignalConfirmation,
    ) -> ConfirmationReplayOutput:
        """Replay confirmation through the canonical Backtest integration boundary."""
        return self.confirmation_replay.run(requests, confirmer)

    def replay_market_structure(
        self,
        requests: tuple[MarketStructureRequest, ...],
        evaluator: MarketStructureEvaluator,
    ) -> MarketStructureReplayOutput:
        """Replay market structure through the canonical Backtest integration boundary."""
        return self.market_structure_replay.run(requests, evaluator)
