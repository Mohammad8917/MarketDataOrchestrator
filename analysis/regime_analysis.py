"""FILE: analysis/regime_analysis.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-30
DATE_PERSIAN: 1405-07-08
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compose deterministic regime features, classification, uncertainty, and volatility state for point-in-time analysis.
LAYER: analysis
OWNS: Regime analysis orchestration and immutable aggregate output semantics.
DOES_NOT_OWN: provider I/O, persistence mutation, strategy selection, risk decisions, or execution.
DEPENDENCIES: dataclasses, datetime, regime.features.regime_feature_builder, regime.features.regime_features, regime.classification.rule_based_classifier, regime.classification.regime_classifier, regime.uncertainty.regime_uncertainty, volatility.state.volatility_state
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from regime.classification.regime_classifier import RegimeOutput, RegimeRequest
from regime.classification.rule_based_classifier import RuleBasedRegimeClassifier
from regime.features.regime_feature_builder import DeterministicCloseReturnFeatureBuilder
from regime.features.regime_features import RegimeFeatureRequest, RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import (
    ConfidenceComplementUncertaintyEvaluator,
    RegimeUncertaintyOutput,
    RegimeUncertaintyRequest,
)
from volatility.state.volatility_state import (
    NormalizedRegimeVolatilityEvaluator,
    VolatilityStateOutput,
    VolatilityStateRequest,
)

CONTRACT_ID = "regime_analysis_boundary"
CONTRACT_VERSION = "1.0.0"
METHODOLOGY_ID = "deterministic_regime_analysis_baseline"
METHODOLOGY_VERSION = "1.0.0"


def _utc(value: object, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")
    return value


@dataclass(frozen=True, slots=True)
class RegimeAnalysisOutput:
    features: RegimeFeatureSet
    classification: RegimeOutput
    uncertainty: RegimeUncertaintyOutput
    volatility_state: VolatilityStateOutput
    event_time: datetime
    received_at: datetime
    source_event_id: str
    contract_version: str = CONTRACT_VERSION

    def __post_init__(self) -> None:
        event_time = _utc(self.event_time, "event_time")
        received_at = _utc(self.received_at, "received_at")
        if received_at < event_time:
            raise ValueError("received_at must not precede event_time")
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        if self.features.event_time != event_time:
            raise ValueError("features event_time must match analysis event_time")
        if self.features.source_event_id != self.source_event_id:
            raise ValueError("features source_event_id must match analysis source_event_id")
        if self.classification.event_time != event_time:
            raise ValueError("classification event_time must match analysis event_time")
        if self.uncertainty.event_time != event_time:
            raise ValueError("uncertainty event_time must match analysis event_time")
        if self.uncertainty.source_event_id != self.source_event_id:
            raise ValueError("uncertainty source_event_id must match analysis source_event_id")
        if self.volatility_state.event_time != event_time:
            raise ValueError("volatility_state event_time must match analysis event_time")
        if self.volatility_state.received_at != received_at:
            raise ValueError("volatility_state received_at must match analysis received_at")
        if self.volatility_state.source_event_id != self.source_event_id:
            raise ValueError("volatility_state source_event_id must match analysis source_event_id")


@runtime_checkable
class RegimeAnalysisEvaluator(Protocol):
    contract_id: str
    contract_version: str
    methodology_id: str
    methodology_version: str

    def analyze(self, request: RegimeFeatureRequest) -> RegimeAnalysisOutput: ...


class DeterministicRegimeAnalysisEvaluator:
    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION
    methodology_id = METHODOLOGY_ID
    methodology_version = METHODOLOGY_VERSION

    def __init__(self) -> None:
        self._feature_builder = DeterministicCloseReturnFeatureBuilder()
        self._classifier = RuleBasedRegimeClassifier()
        self._uncertainty = ConfidenceComplementUncertaintyEvaluator()
        self._volatility_state = NormalizedRegimeVolatilityEvaluator()

    def analyze(self, request: RegimeFeatureRequest) -> RegimeAnalysisOutput:
        features = self._feature_builder.build(request)
        classification = self._classifier.classify(
            RegimeRequest(
                features={
                    "trend_score": (features.trend_score,),
                    "volatility_score": (features.volatility_score,),
                },
                event_time=features.event_time,
                received_at=request.received_at,
                source_event_id=features.source_event_id,
            )
        )
        uncertainty: RegimeUncertaintyOutput = self._uncertainty.assess(
            RegimeUncertaintyRequest(
                confidence=classification.confidence,
                event_time=classification.event_time,
                received_at=request.received_at,
                source_event_id=features.source_event_id,
            )
        )
        volatility_state = self._volatility_state.assess(
            VolatilityStateRequest(
                volatility_score=features.volatility_score,
                event_time=features.event_time,
                received_at=request.received_at,
                source_event_id=features.source_event_id,
            )
        )
        return RegimeAnalysisOutput(
            features=features,
            classification=classification,
            uncertainty=uncertainty,
            volatility_state=volatility_state,
            event_time=request.event_time,
            received_at=request.received_at,
            source_event_id=request.source_event_id,
        )
