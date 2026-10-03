from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backtest.regime_analyzer import RegimeAnalysisReplay
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def make_events(count: int) -> tuple[MarketDataEvent, ...]:
    return tuple(
        MarketDataEvent.create(
            provider="test",
            symbol="BTCUSDT",
            timeframe=Timeframe.parse("1m"),
            event_time=NOW + timedelta(minutes=index),
            received_at=NOW + timedelta(minutes=index),
            open=Decimal(str(100 + index)),
            high=Decimal(str(101 + index)),
            low=Decimal(str(99 + index)),
            close=Decimal(str(100 + index)),
            volume=Decimal("1"),
        )
        for index in range(count)
    )


def test_replay_uses_only_history_available_at_each_event() -> None:
    events = make_events(6)
    result = RegimeAnalysisReplay(
        trend_lookback=4,
        volatility_short_lookback=2,
        volatility_long_lookback=4,
    ).run(events)

    assert len(result.results) == 3
    assert [item.event_time for item in result.results] == [
        NOW + timedelta(minutes=index) for index in (3, 4, 5)
    ]
    assert [item.source_event_id for item in result.results] == [
        str(event.event_id) for event in events[3:]
    ]


def test_replay_is_deterministic() -> None:
    events = make_events(6)
    replay = RegimeAnalysisReplay(
        trend_lookback=4,
        volatility_short_lookback=2,
        volatility_long_lookback=4,
    )
    assert replay.run(events) == replay.run(events)


def test_replay_rejects_unordered_events() -> None:
    events = make_events(6)
    with pytest.raises(ValueError, match="strictly ordered"):
        RegimeAnalysisReplay(
            trend_lookback=4,
            volatility_short_lookback=2,
            volatility_long_lookback=4,
        ).run((events[0], events[2], events[1], *events[3:]))


def test_replay_rejects_insufficient_history() -> None:
    with pytest.raises(ValueError, match="insufficient history"):
        RegimeAnalysisReplay(
            trend_lookback=4,
            volatility_short_lookback=2,
            volatility_long_lookback=4,
        ).run(make_events(3))


def test_replay_rejects_invalid_event_container() -> None:
    with pytest.raises(ValueError, match="events must be a tuple"):
        RegimeAnalysisReplay().run([])  # type: ignore[arg-type]


def test_replay_rejects_invalid_event_element() -> None:
    events = make_events(30)
    with pytest.raises(ValueError, match="events must contain only MarketDataEvent"):
        RegimeAnalysisReplay().run((*events[:-1], object()))  # type: ignore[arg-type]


def test_replay_rejects_invalid_evaluator() -> None:
    with pytest.raises(TypeError, match="must implement RegimeAnalysisEvaluator"):
        RegimeAnalysisReplay(evaluator=object())  # type: ignore[arg-type]


def test_replay_rejects_invalid_output_type() -> None:
    from typing import cast
    from analysis.regime_analysis import RegimeAnalysisOutput

    class InvalidEvaluator:
        contract_id = "test"
        contract_version = "1.0.0"
        methodology_id = "test"
        methodology_version = "1.0.0"

        def analyze(self, request: object) -> RegimeAnalysisOutput:
            return cast(RegimeAnalysisOutput, object())

    events = make_events(30)
    with pytest.raises(TypeError, match="must return RegimeAnalysisOutput"):
        RegimeAnalysisReplay(evaluator=InvalidEvaluator()).run(events)  # type: ignore[arg-type]


def test_replay_rejects_temporally_misaligned_output() -> None:
    class MisalignedEvaluator:
        contract_id = "test"
        contract_version = "1.0.0"
        methodology_id = "test"
        methodology_version = "1.0.0"

        def analyze(self, request):
            from dataclasses import replace
            from analysis.regime_analysis import DeterministicRegimeAnalysisEvaluator

            result = DeterministicRegimeAnalysisEvaluator().analyze(request)
            shifted = result.event_time + timedelta(minutes=1)
            return replace(result, event_time=shifted, received_at=shifted)

    events = make_events(30)
    with pytest.raises(ValueError, match="event_time must match"):
        RegimeAnalysisReplay(evaluator=MisalignedEvaluator()).run(events)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"trend_lookback": 1}, "trend_lookback must be >= 2"),
        ({"volatility_short_lookback": 1}, "volatility_short_lookback must be >= 2"),
        (
            {"volatility_short_lookback": 4, "volatility_long_lookback": 4},
            "volatility_long_lookback must exceed volatility_short_lookback",
        ),
    ],
)
def test_replay_rejects_invalid_lookback_configuration(
    kwargs: dict[str, int], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        RegimeAnalysisReplay(**kwargs)


def test_replay_rejects_empty_tuple() -> None:
    with pytest.raises(ValueError, match="events must not be empty"):
        RegimeAnalysisReplay().run(())


def test_replay_rejects_received_at_mismatch() -> None:
    class MisalignedEvaluator:
        contract_id = "test"
        contract_version = "1.0.0"
        methodology_id = "test"
        methodology_version = "1.0.0"

        def analyze(self, request):
            from dataclasses import replace
            from analysis.regime_analysis import DeterministicRegimeAnalysisEvaluator

            result = DeterministicRegimeAnalysisEvaluator().analyze(request)
            return replace(result, received_at=request.received_at + timedelta(minutes=1))

    with pytest.raises(ValueError, match="received_at must match"):
        RegimeAnalysisReplay(evaluator=MisalignedEvaluator()).run(make_events(30))


def test_replay_rejects_source_event_id_mismatch() -> None:
    class MisalignedEvaluator:
        contract_id = "test"
        contract_version = "1.0.0"
        methodology_id = "test"
        methodology_version = "1.0.0"

        def analyze(self, request):
            from dataclasses import replace
            from analysis.regime_analysis import DeterministicRegimeAnalysisEvaluator

            result = DeterministicRegimeAnalysisEvaluator().analyze(request)
            return replace(result, source_event_id="different-event")

    with pytest.raises(ValueError, match="source_event_id must match"):
        RegimeAnalysisReplay(evaluator=MisalignedEvaluator()).run(make_events(30))
