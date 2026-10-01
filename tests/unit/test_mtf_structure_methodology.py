"""Verify deterministic multi-timeframe structure alignment methodology."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from analysis.mtf.deterministic_latest_point_alignment import (
    DeterministicLatestPointAlignment,
)
from shared.contracts.market_structure import MarketStructureOutput, StructurePoint
from shared.contracts.mtf_structure import MtfStructureInput, MtfStructureRequest


def _structure(moment, source, kinds=()):
    points = tuple(
        StructurePoint(
            kind,
            moment + timedelta(minutes=index),
            f"{source}-{index}",
            Decimal("100"),
        )
        for index, kind in enumerate(kinds)
    )
    return MarketStructureOutput(points, (), None, moment, source)


def _request(items):
    moment = datetime(2026, 1, 1, tzinfo=UTC)
    return MtfStructureRequest(
        tuple(
            MtfStructureInput(name, _structure(moment, name, kinds))
            for name, kinds in items
        ),
        moment,
        moment,
        "mtf-1",
    )


def test_bullish_alignment_from_latest_higher_points() -> None:
    output = DeterministicLatestPointAlignment().evaluate(
        _request((("higher", ("HH", "HL")), ("execution", ("HH",))))
    )
    assert output.alignment == "bullish"
    assert [item.direction for item in output.observations] == ["bullish", "bullish"]


def test_bearish_alignment_and_mixed_alignment() -> None:
    evaluator = DeterministicLatestPointAlignment()
    bearish = evaluator.evaluate(
        _request((("higher", ("LH", "LL")), ("execution", ("LL",))))
    )
    mixed = evaluator.evaluate(
        _request((("higher", ("HH",)), ("execution", ("LL",))))
    )
    assert bearish.alignment == "bearish"
    assert mixed.alignment == "mixed"


def test_unknown_timeframes_do_not_create_direction() -> None:
    output = DeterministicLatestPointAlignment().evaluate(
        _request((("higher", ()), ("execution", ("HH",))))
    )
    assert output.alignment == "bullish"
    assert [item.direction for item in output.observations] == ["unknown", "bullish"]


def test_conflicting_points_at_latest_time_are_unknown() -> None:
    moment = datetime(2026, 1, 1, tzinfo=UTC)
    structure = MarketStructureOutput(
        (
            StructurePoint("HH", moment, "a", Decimal("100")),
            StructurePoint("LL", moment, "b", Decimal("99")),
        ),
        (),
        None,
        moment,
        "source",
    )
    request = MtfStructureRequest(
        (MtfStructureInput("higher", structure),),
        moment,
        moment,
        "mtf-1",
    )
    output = DeterministicLatestPointAlignment().evaluate(request)
    assert output.observations[0].direction == "unknown"
    assert output.alignment == "insufficient"
