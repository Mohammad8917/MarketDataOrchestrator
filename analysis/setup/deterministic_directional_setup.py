"""FILE: analysis/setup/deterministic_directional_setup.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Provide a deterministic, market-agnostic setup methodology from normalized analytical evidence.
LAYER: analysis
OWNS: Directional setup classification and bounded setup strength from canonical evidence.
DOES_NOT_OWN: signal generation, confirmation finalization, cost, liquidity, risk, decision, provider I/O, persistence
DEPENDENCIES: stdlib:math; shared.interfaces.setup
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0

Methodology v1:
- Every input value is normalized evidence in [-1.0, 1.0].
- The arithmetic mean is the deterministic aggregate; input names have no semantic weighting.
- Bullish setup requires mean >= 0.5.
- Bearish setup requires mean <= -0.5.
- Otherwise the setup is neutral.
- Strength is the absolute aggregate, bounded to [0.0, 1.0].
- Empty, non-finite, or out-of-range evidence is invalid.
- No market, provider, timeframe, execution, cost, liquidity, risk, or decision semantics are embedded.
- A setup is an analytical observation, not a trading instruction or profitability claim.
"""

from math import isfinite

from shared.interfaces.setup import (
    SETUP_CONTRACT_ID,
    SETUP_CONTRACT_VERSION,
    SetupOutput,
    SetupRequest,
    SetupDirection,
)

SETUP_METHODOLOGY_ID = "deterministic_directional_setup_v1"
SETUP_METHODOLOGY_VERSION = "1.0.0"
SETUP_DIRECTION_THRESHOLD = 0.5


class DeterministicDirectionalSetup:
    """Classify normalized evidence into a bounded directional setup observation."""

    contract_id = SETUP_CONTRACT_ID
    contract_version = SETUP_CONTRACT_VERSION
    setup_id = SETUP_METHODOLOGY_ID

    def evaluate(self, request: SetupRequest) -> SetupOutput:
        values = tuple(request.inputs.values())
        self._validate_values(values)

        aggregate = sum(values) / len(values)
        direction: SetupDirection
        if aggregate >= SETUP_DIRECTION_THRESHOLD:
            direction = "bullish"
        elif aggregate <= -SETUP_DIRECTION_THRESHOLD:
            direction = "bearish"
        else:
            direction = "neutral"

        return SetupOutput(
            direction=direction,
            strength=abs(aggregate),
            event_time=request.event_time,
            setup_id=self.setup_id,
        )

    @staticmethod
    def _validate_values(values: tuple[float, ...]) -> None:
        if not values:
            raise ValueError("inputs must not be empty")
        for value in values:
            if not isfinite(value):
                raise ValueError("inputs must contain only finite values")
            if not -1.0 <= value <= 1.0:
                raise ValueError("inputs must be within [-1.0, 1.0]")
