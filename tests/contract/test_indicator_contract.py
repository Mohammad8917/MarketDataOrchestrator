"""FILE: tests/contract/test_indicator_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the typed indicator execution contract and its temporal boundary behavior.
LAYER: tests
OWNS: Indicator contract acceptance and rejection cases for the canonical indicator protocol.
DOES_NOT_OWN: production indicator algorithms, production state, provider I/O
DEPENDENCIES: indicators.core.base; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import UTC, datetime
from typing import Any

import pytest

from indicators.core.base import (
    INDICATOR_CONTRACT_ID,
    INDICATOR_CONTRACT_VERSION,
    Indicator,
    IndicatorOutput,
    IndicatorRequest,
)


class _FakeIndicator:
    contract_id = INDICATOR_CONTRACT_ID
    contract_version = INDICATOR_CONTRACT_VERSION
    indicator_id = "test.fake"

    def calculate(self, request: IndicatorRequest) -> IndicatorOutput:
        return IndicatorOutput(
            values={"value": float(request.series["close"][-1])},
            event_time=request.event_time,
            indicator_id=self.indicator_id,
        )


def _request() -> IndicatorRequest:
    now = datetime(2026, 9, 24, 7, 0, tzinfo=UTC)
    return IndicatorRequest(
        series={"close": (100.0, 101.0)},
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
    )


def test_indicator_protocol_is_structurally_implemented() -> None:
    indicator = _FakeIndicator()
    assert isinstance(indicator, Indicator)
    assert indicator.contract_id == INDICATOR_CONTRACT_ID
    assert indicator.contract_version == INDICATOR_CONTRACT_VERSION


def test_output_rejects_empty_indicator_id() -> None:
    now = datetime(2026, 9, 24, 7, tzinfo=UTC)
    with pytest.raises(ValueError, match="indicator_id"):
        IndicatorOutput({"value": 1.0}, now, "")


def test_indicator_contract_returns_typed_output() -> None:
    result = _FakeIndicator().calculate(_request())
    assert isinstance(result, IndicatorOutput)
    assert result.values == {"value": 101.0}
    assert result.event_time.tzinfo is UTC
    assert result.indicator_id == "test.fake"


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_indicator_request_rejects_naive_datetime(field: str) -> None:
    values: dict[str, Any] = {
        "series": {"close": (100.0,)},
        "event_time": datetime(2026, 9, 24, 7, 0, tzinfo=UTC),
        "received_at": datetime(2026, 9, 24, 7, 0, tzinfo=UTC),
        "source_event_id": "evt-1",
    }
    values[field] = datetime(2026, 9, 24, 7, 0)
    with pytest.raises(ValueError, match="timezone-aware UTC"):
        IndicatorRequest(**values)


def test_indicator_request_rejects_empty_source_event_id() -> None:
    with pytest.raises(ValueError, match="source_event_id"):
        IndicatorRequest(
            series={"close": (100.0,)},
            event_time=datetime(2026, 9, 24, 7, 0, tzinfo=UTC),
            received_at=datetime(2026, 9, 24, 7, 0, tzinfo=UTC),
            source_event_id="",
        )
