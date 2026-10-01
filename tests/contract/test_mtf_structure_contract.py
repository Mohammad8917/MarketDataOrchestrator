"""Verify the multi-timeframe market-structure contract invariants."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from shared.contracts.market_structure import MarketStructureOutput, StructurePoint
from shared.contracts.mtf_structure import (
    MTF_STRUCTURE_CONTRACT_ID,
    MTF_STRUCTURE_CONTRACT_VERSION,
    MtfStructureInput,
    MtfStructureObservation,
    MtfStructureOutput,
    MtfStructureRequest,
)


def _structure(moment: datetime, source: str, kind: str = "HH") -> MarketStructureOutput:
    point = StructurePoint(kind, moment, source, Decimal("100"))
    return MarketStructureOutput((point,), (), None, moment, source)


def _request() -> MtfStructureRequest:
    moment = datetime(2026, 1, 1, tzinfo=UTC)
    return MtfStructureRequest(
        (
            MtfStructureInput("higher", _structure(moment, "higher")),
            MtfStructureInput("execution", _structure(moment, "execution")),
        ),
        moment,
        moment,
        "mtf-1",
    )


def test_contract_identity_and_immutable_values() -> None:
    request = _request()
    output = MtfStructureOutput(
        (
            MtfStructureObservation("higher", "bullish"),
            MtfStructureObservation("execution", "bearish"),
        ),
        "mixed",
        request.event_time,
        request.source_event_id,
    )
    assert MTF_STRUCTURE_CONTRACT_ID == "mtf_structure_alignment_boundary"
    assert MTF_STRUCTURE_CONTRACT_VERSION == "1.0.0"
    assert output.observations[0].direction == "bullish"
    with pytest.raises(AttributeError):
        output.alignment = "bullish"  # type: ignore[misc]


def test_request_rejects_duplicate_timeframes() -> None:
    moment = datetime(2026, 1, 1, tzinfo=UTC)
    structure = _structure(moment, "event")
    with pytest.raises(ValueError, match="unique"):
        MtfStructureRequest(
            (
                MtfStructureInput("higher", structure),
                MtfStructureInput("higher", structure),
            ),
            moment,
            moment,
            "mtf-1",
        )


def test_request_rejects_future_structure() -> None:
    moment = datetime(2026, 1, 1, tzinfo=UTC)
    future = moment + timedelta(minutes=1)
    with pytest.raises(ValueError, match="future"):
        MtfStructureRequest(
            (MtfStructureInput("higher", _structure(future, "future")),),
            moment,
            future,
            "mtf-1",
        )


def test_output_rejects_duplicate_observations() -> None:
    moment = datetime(2026, 1, 1, tzinfo=UTC)
    with pytest.raises(ValueError, match="unique"):
        MtfStructureOutput(
            (
                MtfStructureObservation("higher", "bullish"),
                MtfStructureObservation("higher", "bearish"),
            ),
            "mixed",
            moment,
            "mtf-1",
        )
