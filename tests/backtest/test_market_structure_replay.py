"""FILE: tests/backtest/test_market_structure_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify fail-closed market-structure replay validation and temporal identity alignment.
LAYER: tests
OWNS: MarketStructureReplay runtime-boundary and temporal contract verification.
DOES_NOT_OWN: Structure methodology or trading execution.
DEPENDENCIES: backtest.market_structure_replay; shared.contracts.market_structure; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import cast

import pytest

from backtest.market_structure_replay import MarketStructureReplay
from shared.contracts.market_structure import (
    MarketStructureBar,
    MarketStructureOutput,
    MarketStructureRequest,
)


def request(event_id: str = "event-1") -> MarketStructureRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bar = MarketStructureBar(
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=event_id,
        open=Decimal("10"),
        high=Decimal("11"),
        low=Decimal("9"),
        close=Decimal("10"),
        volume=Decimal("1"),
    )
    return MarketStructureRequest(
        bars=(bar,),
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=event_id,
    )


def output(value: MarketStructureRequest) -> MarketStructureOutput:
    return MarketStructureOutput(
        points=(),
        events=(),
        state=None,
        event_time=value.event_time,
        source_event_id=value.source_event_id,
    )


class ValidEvaluator:
    contract_id = "test_market_structure"
    contract_version = "1.0.0"

    def evaluate(self, value: MarketStructureRequest) -> MarketStructureOutput:
        return output(value)


def test_replays_valid_request() -> None:
    result = MarketStructureReplay().run((request(),), ValidEvaluator())
    assert result.results == (output(request()),)


@pytest.mark.parametrize("requests", [[], None, "requests"])
def test_rejects_invalid_request_containers(requests: object) -> None:
    with pytest.raises(ValueError, match="requests must be a tuple"):
        MarketStructureReplay().run(requests, ValidEvaluator())  # type: ignore[arg-type]


def test_rejects_invalid_request_element() -> None:
    with pytest.raises(ValueError, match="requests must contain only MarketStructureRequest"):
        MarketStructureReplay().run((request(), object()), ValidEvaluator())  # type: ignore[arg-type]


def test_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="requests must not be empty"):
        MarketStructureReplay().run((), ValidEvaluator())


def test_rejects_invalid_evaluator() -> None:
    with pytest.raises(TypeError, match="must implement MarketStructureEvaluator"):
        MarketStructureReplay().run((request(),), object())  # type: ignore[arg-type]


def test_rejects_invalid_output_type() -> None:
    class InvalidEvaluator(ValidEvaluator):
        def evaluate(self, value: MarketStructureRequest) -> MarketStructureOutput:
            return cast(MarketStructureOutput, object())

    with pytest.raises(TypeError, match="must return MarketStructureOutput"):
        MarketStructureReplay().run((request(),), InvalidEvaluator())


def test_rejects_temporally_misaligned_output() -> None:
    class MisalignedEvaluator(ValidEvaluator):
        def evaluate(self, value: MarketStructureRequest) -> MarketStructureOutput:
            timestamp = datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc)
            return MarketStructureOutput(
                points=(),
                events=(),
                state=None,
                event_time=timestamp,
                source_event_id=value.source_event_id,
            )

    with pytest.raises(ValueError, match="event_time must match"):
        MarketStructureReplay().run((request(),), MisalignedEvaluator())


def test_rejects_source_identity_mismatch() -> None:
    class MisidentifiedEvaluator(ValidEvaluator):
        def evaluate(self, value: MarketStructureRequest) -> MarketStructureOutput:
            return MarketStructureOutput(
                points=(),
                events=(),
                state=None,
                event_time=value.event_time,
                source_event_id="wrong-source",
            )

    with pytest.raises(ValueError, match="source_event_id must match"):
        MarketStructureReplay().run((request(),), MisidentifiedEvaluator())
