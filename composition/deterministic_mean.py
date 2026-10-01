"""FILE: composition/deterministic_mean.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Provide the first executable, deterministic, market-agnostic signal composition methodology.
LAYER: composition
OWNS: Bounded equal-weight composition of normalized analytical evidence.
DOES_NOT_OWN: signal generation, regime classification, setup detection, decision finalization, risk, provider I/O, persistence
DEPENDENCIES: composition.composer
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0

Methodology v1:
- Each upstream signal is normalized evidence in [-1.0, 1.0].
- Every signal has equal weight; signal names do not affect the result.
- The composed value is the arithmetic mean of all supplied signals.
- Empty input is invalid.
- Non-finite values and values outside [-1.0, 1.0] are invalid.
- Output is therefore bounded to [-1.0, 1.0].
- No market, provider, timeframe, execution, cost, risk, or decision semantics are embedded here.
"""

from math import isfinite

from composition.composer import (
    COMPOSITION_CONTRACT_ID,
    COMPOSITION_CONTRACT_VERSION,
    CompositionOutput,
    CompositionRequest,
)

COMPOSITION_METHODOLOGY_ID = "deterministic_equal_weight_mean_v1"
COMPOSITION_METHODOLOGY_VERSION = "1.0.0"


class DeterministicEqualWeightMeanComposer:
    """Compose normalized analytical evidence with equal deterministic weights."""

    contract_id = COMPOSITION_CONTRACT_ID
    contract_version = COMPOSITION_CONTRACT_VERSION
    composition_id = COMPOSITION_METHODOLOGY_ID

    def compose(self, request: CompositionRequest) -> CompositionOutput:
        if not request.signals:
            raise ValueError("signals must not be empty")

        values = tuple(request.signals.values())
        for value in values:
            if not isfinite(value):
                raise ValueError("signals must contain only finite values")
            if not -1.0 <= value <= 1.0:
                raise ValueError("signals must be within [-1.0, 1.0]")

        value = sum(values) / len(values)
        return CompositionOutput(
            value=value,
            event_time=request.event_time,
            composition_id=self.composition_id,
        )
