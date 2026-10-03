"""FILE: tests/backtest/test_mtf_structure_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify fail-closed MTF replay validation and temporal/source identity alignment.
LAYER: tests
OWNS: MtfStructureReplay runtime-boundary and temporal contract verification.
DOES_NOT_OWN: Structure methodology or trading execution.
DEPENDENCIES: backtest.mtf_structure_replay; shared.contracts.mtf_structure; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from typing import cast

import pytest

from backtest.mtf_structure_replay import MtfStructureReplay
from shared.contracts.mtf_structure import (
    MtfStructureInput,
    MtfStructureObservation,
    MtfStructureOutput,
    MtfStructureRequest,
)
from shared.contracts.market_structure import MarketStructureOutput


def request(index: int = 0) -> MtfStructureRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    structure = MarketStructureOutput(
        points=(),
        events=(),
        state=None,
        event_time=timestamp,
        source_event_id=f"structure-{index}",
    )
    return MtfStructureRequest(
        inputs=(MtfStructureInput(timeframe="1h", structure=structure),),
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"event-{index}",
    )


def output(value: MtfStructureRequest) -> MtfStructureOutput:
    return MtfStructureOutput(
        observations=(MtfStructureObservation(timeframe="1h", direction="bullish"),),
        alignment="bullish",
        event_time=value.event_time,
        source_event_id=value.source_event_id,
    )


class ValidEvaluator:
    contract_id = "test_mtf_structure"
    contract_version = "1.0.0"

    def evaluate(self, value: MtfStructureRequest) -> MtfStructureOutput:
        return output(value)


def test_replays_ordered_requests() -> None:
    result = MtfStructureReplay().run((request(0), request(1)), ValidEvaluator())
    assert result.results == (output(request(0)), output(request(1)))


@pytest.mark.parametrize("requests", [[], None, "requests"])
def test_rejects_invalid_request_containers(requests: object) -> None:
    with pytest.raises(ValueError, match="requests must be a tuple"):
        MtfStructureReplay().run(requests, ValidEvaluator())  # type: ignore[arg-type]


def test_rejects_invalid_request_element() -> None:
    with pytest.raises(ValueError, match="requests must contain only MtfStructureRequest"):
        MtfStructureReplay().run((request(), object()), ValidEvaluator())  # type: ignore[arg-type]


def test_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="requests must not be empty"):
        MtfStructureReplay().run((), ValidEvaluator())


def test_rejects_non_strict_temporal_order() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        MtfStructureReplay().run((request(1), request(0)), ValidEvaluator())


def test_rejects_invalid_evaluator() -> None:
    with pytest.raises(TypeError, match="must implement MtfStructureEvaluator"):
        MtfStructureReplay().run((request(),), object())  # type: ignore[arg-type]


def test_rejects_invalid_output_type() -> None:
    class InvalidEvaluator(ValidEvaluator):
        def evaluate(self, value: MtfStructureRequest) -> MtfStructureOutput:
            return cast(MtfStructureOutput, object())

    with pytest.raises(TypeError, match="must return MtfStructureOutput"):
        MtfStructureReplay().run((request(),), InvalidEvaluator())


def test_rejects_temporally_misaligned_output() -> None:
    class MisalignedEvaluator(ValidEvaluator):
        def evaluate(self, value: MtfStructureRequest) -> MtfStructureOutput:
            return MtfStructureOutput(
                observations=(MtfStructureObservation(timeframe="1h", direction="bullish"),),
                alignment="bullish",
                event_time=value.event_time + timedelta(minutes=1),
                source_event_id=value.source_event_id,
            )

    with pytest.raises(ValueError, match="event_time must match"):
        MtfStructureReplay().run((request(),), MisalignedEvaluator())


def test_rejects_source_identity_mismatch() -> None:
    class MisidentifiedEvaluator(ValidEvaluator):
        def evaluate(self, value: MtfStructureRequest) -> MtfStructureOutput:
            return MtfStructureOutput(
                observations=(MtfStructureObservation(timeframe="1h", direction="bullish"),),
                alignment="bullish",
                event_time=value.event_time,
                source_event_id="wrong-source",
            )

    with pytest.raises(ValueError, match="source_event_id must match"):
        MtfStructureReplay().run((request(),), MisidentifiedEvaluator())
