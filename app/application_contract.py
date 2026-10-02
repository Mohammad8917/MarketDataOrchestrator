"""FILE: app/application_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the typed application request boundary for opportunity orchestration.
LAYER: app
OWNS: Application request shape and local lifecycle-input invariants only.
DOES_NOT_OWN: analytical methodology, safety approval, risk allocation, execution, persistence, or delivery.
DEPENDENCIES: analysis.regime_analysis, composition.confirmation_contract, shared.contracts.cost, shared.contracts.liquidity, shared.contracts.pretrade_safety, shared.interfaces.setup, shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass

from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.interfaces.setup import SetupOutput
from shared.models.decision import DecisionOutput


@dataclass(frozen=True, slots=True)
class ApplicationRequest:
    """Immutable application input assembled from canonical analytical boundaries."""

    decision: DecisionOutput
    safety: PreTradeSafetyOutput
    setup: SetupOutput
    confirmation: ConfirmationOutput
    regime: RegimeAnalysisOutput
    cost: CostOutput
    liquidity: LiquidityOutput
    liquidity_quality: float
    cost_efficiency: float
    limit: int

    def __post_init__(self) -> None:
        for name in ("liquidity_quality", "cost_efficiency"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.limit < 1:
            raise ValueError("limit must be at least 1")
