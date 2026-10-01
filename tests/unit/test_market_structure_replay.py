"""Verify point-in-time market-structure replay behavior."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from backtest.market_structure_replay import MarketStructureReplay
from shared.contracts.market_structure import (
    MarketStructureBar,
    MarketStructureOutput,
    MarketStructureRequest,
)


class StubEvaluator:
    contract_id = "market_structure_boundary"
    contract_version = "1.0.0"

    def evaluate(self, request: MarketStructureRequest) -> MarketStructureOutput:
        return MarketStructureOutput((), (), None, request.event_time, request.source_event_id)


def _request(index: int) -> MarketStructureRequest:
    moment = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index)
    bar = MarketStructureBar(
        event_time=moment,
        received_at=moment,
        source_event_id=f"evt-{index}",
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("1"),
    )
    return MarketStructureRequest((bar,), moment, moment, f"evt-{index}")


def test_replay_identity_and_immutable_output() -> None:
    replay = MarketStructureReplay()
    output = replay.run((_request(0), _request(1)), StubEvaluator())
    assert replay.contract_id == "backtest_market_structure_replay_boundary"
    assert replay.contract_version == "1.0.0"
    assert isinstance(output.results, tuple)
    assert [item.source_event_id for item in output.results] == ["evt-0", "evt-1"]


def test_replay_rejects_empty_or_non_monotonic_requests() -> None:
    replay = MarketStructureReplay()
    with pytest.raises(ValueError, match="must not be empty"):
        replay.run((), StubEvaluator())
    with pytest.raises(ValueError, match="strictly ordered"):
        replay.run((_request(1), _request(0)), StubEvaluator())


def test_replay_rejects_non_evaluator() -> None:
    with pytest.raises(TypeError, match="MarketStructureEvaluator"):
        MarketStructureReplay().run((_request(0),), object())  # type: ignore[arg-type]


def test_replay_rejects_timestamp_mismatch() -> None:
    class BadEvaluator(StubEvaluator):
        def evaluate(self, request: MarketStructureRequest) -> MarketStructureOutput:
            return MarketStructureOutput(
                (),
                (),
                None,
                request.event_time + timedelta(minutes=1),
                request.source_event_id,
            )

    with pytest.raises(ValueError, match="event_time"):
        MarketStructureReplay().run((_request(0),), BadEvaluator())


def test_replay_rejects_source_event_mismatch() -> None:
    class BadEvaluator(StubEvaluator):
        def evaluate(self, request: MarketStructureRequest) -> MarketStructureOutput:
            return MarketStructureOutput((), (), None, request.event_time, "wrong-event")

    with pytest.raises(ValueError, match="source_event_id"):
        MarketStructureReplay().run((_request(0),), BadEvaluator())
