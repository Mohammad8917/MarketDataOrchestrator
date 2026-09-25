"""FILE: tests/unit/test_indicators.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic indicator implementations at their contract boundary.
LAYER: tests
OWNS: Unit coverage for implemented indicator behavior.
DOES_NOT_OWN: provider I/O, integration orchestration, release approval
DEPENDENCIES: indicators.core.base; indicators.trend.sma; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import cast

import pytest

from indicators.core.base import IndicatorRequest
from indicators.momentum.macd import MovingAverageConvergenceDivergence
from indicators.momentum.rsi import RelativeStrengthIndex
from indicators.volatility.atr import AverageTrueRange
from indicators.volatility.bollinger_bands import BollingerBands
from indicators.volatility.donchian_channels import DonchianChannels
from indicators.trend.ema import ExponentialMovingAverage
from indicators.trend.sma import SimpleMovingAverage


def _request(series: dict[str, list[float]]) -> IndicatorRequest:
    now = datetime(2026, 9, 24, 12, tzinfo=timezone.utc)
    return IndicatorRequest(
        series=series,
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
    )


def test_sma_rejects_non_positive_period() -> None:
    with pytest.raises(ValueError, match="^period must be positive$"):
        SimpleMovingAverage(0)


def test_sma_calculates_last_window_only() -> None:
    output = SimpleMovingAverage(3).calculate(_request({"close": [1.0, 2.0, 3.0, 10.0]}))
    assert output.values == {"sma": 5.0}
    assert output.indicator_id == "sma"


def test_sma_contract_is_final_window_not_rolling_series() -> None:
    output = SimpleMovingAverage(3).calculate(_request({"close": [1.0, 2.0, 3.0, 4.0, 5.0]}))
    assert output.values == {"sma": 4.0}
    assert list(output.values) == ["sma"]


def test_sma_matches_independent_reference_dataset() -> None:
    reference_path = Path(__file__).resolve().parents[1] / "fixtures" / "sma_reference.csv"
    with reference_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    actual = []
    for row in rows:
        series = [float(value) for value in row["input"].split("|")]
        period = int(row["period"])
        output = SimpleMovingAverage(period).calculate(_request({"close": series}))
        actual.append(output.values["sma"])

    expected = [float(row["expected_sma"]) for row in rows]
    assert actual == expected


def test_sma_period_one_returns_input() -> None:
    output = SimpleMovingAverage(1).calculate(_request({"close": [7.25]}))
    assert output.values == {"sma": 7.25}


def test_sma_rejects_empty_series() -> None:
    with pytest.raises(ValueError, match="^close series must not be empty$"):
        SimpleMovingAverage(3).calculate(_request({"close": []}))


def test_sma_rejects_non_finite_input() -> None:
    for value in (float("nan"), float("inf"), float("-inf")):
        request = _request({"close": [1.0, 2.0, value]})
        with pytest.raises(ValueError, match="^close series values must be finite numeric values$"):
            SimpleMovingAverage(3).calculate(request)


def test_sma_rejects_boolean_input() -> None:
    request = _request(cast(dict[str, list[float]], {"close": [True, False, True]}))
    with pytest.raises(ValueError, match="^close series values must be finite numeric values$"):
        SimpleMovingAverage(2).calculate(request)


def test_sma_rejects_non_finite_result() -> None:
    request = _request({"close": [1.7e308, 1.7e308, 1.7e308]})
    with pytest.raises(ValueError, match="^SMA result is non-finite$"):
        SimpleMovingAverage(3).calculate(request)


def test_sma_accepts_constant_values() -> None:
    output = SimpleMovingAverage(3).calculate(_request({"close": [5.0, 5.0, 5.0]}))
    assert output.values == {"sma": 5.0}


def test_sma_rejects_missing_close_series() -> None:
    with pytest.raises(ValueError, match="^series must contain close$"):
        SimpleMovingAverage(3).calculate(_request({"open": [1.0, 2.0, 3.0]}))


def test_sma_rejects_short_series() -> None:
    with pytest.raises(ValueError, match="^close series is shorter than period$"):
        SimpleMovingAverage(4).calculate(_request({"close": [1.0, 2.0, 3.0]}))


def test_sma_rejects_non_numeric_window_value() -> None:
    request = _request({"close": [1.0, 2.0, 3.0, 4.0]})
    bad_request = IndicatorRequest(
        series={"close": [1.0, 2.0, 3.0, "bad"]},  # type: ignore[list-item]
        event_time=request.event_time,
        received_at=request.received_at,
        source_event_id=request.source_event_id,
    )
    with pytest.raises(ValueError, match="^close series values must be finite numeric values$"):
        SimpleMovingAverage(3).calculate(bad_request)


def test_sma_exposes_immutable_configuration() -> None:
    indicator = SimpleMovingAverage(3)
    assert indicator.period == 3


def test_ema_matches_reference_value() -> None:
    output = ExponentialMovingAverage(3).calculate(_request({"close": [1.0, 2.0, 3.0, 4.0, 5.0]}))
    assert output.values == {"ema": 4.0}
    assert output.indicator_id == "ema"


def test_ema_rejects_empty_series() -> None:
    with pytest.raises(ValueError, match="^close series must not be empty$"):
        ExponentialMovingAverage(3).calculate(_request({"close": []}))


def test_ema_period_one_returns_latest_value() -> None:
    output = ExponentialMovingAverage(1).calculate(_request({"close": [7.0, 8.0, 9.0]}))
    assert output.values == {"ema": 9.0}


def test_ema_rejects_non_finite_input() -> None:
    request = _request({"close": [1.0, 2.0, float("nan")]})
    with pytest.raises(ValueError, match="^close series values must be finite numeric values$"):
        ExponentialMovingAverage(3).calculate(request)


def test_ema_rejects_period_longer_than_series() -> None:
    with pytest.raises(ValueError, match="^close series is shorter than period$"):
        ExponentialMovingAverage(4).calculate(_request({"close": [1.0, 2.0, 3.0]}))


def test_rsi_matches_wilder_reference_value() -> None:
    output = RelativeStrengthIndex(3).calculate(_request({"close": [1.0, 2.0, 3.0, 2.0, 4.0, 3.0]}))
    assert output.values["rsi"] == pytest.approx(60.6060606060606)
    assert output.indicator_id == "rsi"


def test_rsi_rejects_empty_series() -> None:
    with pytest.raises(ValueError, match="^close series must not be empty$"):
        RelativeStrengthIndex(3).calculate(_request({"close": []}))


def test_rsi_period_one_uses_latest_change() -> None:
    output = RelativeStrengthIndex(1).calculate(_request({"close": [7.0, 8.0, 6.0]}))
    assert output.values == {"rsi": 0.0}


def test_rsi_rejects_non_finite_input() -> None:
    request = _request({"close": [1.0, 2.0, float("nan"), 3.0]})
    with pytest.raises(ValueError, match="^close series values must be finite numeric values$"):
        RelativeStrengthIndex(3).calculate(request)


def test_rsi_rejects_period_longer_than_available_changes() -> None:
    with pytest.raises(ValueError, match="^close series is shorter than period plus one$"):
        RelativeStrengthIndex(4).calculate(_request({"close": [1.0, 2.0, 3.0, 4.0]}))


def test_true_range_uses_previous_close_gap() -> None:
    from indicators.volatility.true_range import true_range

    assert true_range(15.0, 12.0, 10.0) == 5.0


def test_atr_matches_wilder_reference_value() -> None:
    output = AverageTrueRange(2).calculate(
        _request(
            {
                "high": [12.0, 13.0, 15.0, 14.0],
                "low": [10.0, 11.0, 12.0, 11.0],
                "close": [11.0, 12.0, 13.0, 12.0],
            }
        )
    )
    assert output.values["atr"] == pytest.approx(2.75)


def test_atr_rejects_empty_ohlc() -> None:
    with pytest.raises(ValueError, match="^OHLC series must not be empty$"):
        AverageTrueRange(2).calculate(_request({"high": [], "low": [], "close": []}))


def test_atr_rejects_period_longer_than_series() -> None:
    with pytest.raises(ValueError, match="^OHLC series is shorter than period$"):
        AverageTrueRange(4).calculate(
            _request(
                {
                    "high": [12.0, 13.0, 14.0],
                    "low": [10.0, 11.0, 12.0],
                    "close": [11.0, 12.0, 13.0],
                }
            )
        )


def test_true_range_rejects_invalid_high_low_order() -> None:
    from indicators.volatility.true_range import true_range

    with pytest.raises(ValueError, match="^high must be greater than or equal to low$"):
        true_range(10.0, 12.0)


def test_macd_matches_ema_derived_reference() -> None:
    output = MovingAverageConvergenceDivergence(3, 5, 2).calculate(
        _request({"close": [1.0, 2.0, 4.0, 3.0, 5.0, 4.0, 6.0, 7.0, 5.0, 8.0]})
    )
    assert output.values["macd"] == pytest.approx(0.6789480452674903)
    assert output.values["signal"] == pytest.approx(0.6279578189300419)
    assert output.values["histogram"] == pytest.approx(0.05099022633744843)


def test_macd_requires_fast_period_shorter_than_slow_period() -> None:
    with pytest.raises(ValueError, match="^fast period must be shorter than slow period$"):
        MovingAverageConvergenceDivergence(5, 3, 2)


def test_macd_rejects_insufficient_warmup_data() -> None:
    with pytest.raises(ValueError, match="^close series is shorter than MACD warm-up$"):
        MovingAverageConvergenceDivergence(3, 5, 2).calculate(
            _request({"close": [1.0, 2.0, 3.0, 4.0, 5.0]})
        )


def test_donchian_matches_channel_reference() -> None:
    output = DonchianChannels(3).calculate(
        _request(
            {
                "high": [10.0, 12.0, 11.0, 13.0],
                "low": [8.0, 9.0, 9.0, 10.0],
                "close": [9.0, 11.0, 10.0, 12.0],
            }
        )
    )
    assert output.values == {"upper": 13.0, "lower": 9.0, "middle": 11.0, "breakout": 0.0}


def test_donchian_detects_upward_breakout() -> None:
    output = DonchianChannels(3).calculate(
        _request(
            {
                "high": [10.0, 12.0, 11.0, 14.0],
                "low": [8.0, 9.0, 9.0, 10.0],
                "close": [9.0, 11.0, 10.0, 14.0],
            }
        )
    )
    assert output.values["breakout"] == 1.0


def test_donchian_detects_downward_breakout() -> None:
    output = DonchianChannels(3).calculate(
        _request(
            {
                "high": [10.0, 12.0, 11.0, 9.0],
                "low": [8.0, 9.0, 9.0, 7.0],
                "close": [9.0, 11.0, 10.0, 7.0],
            }
        )
    )
    assert output.values["breakout"] == -1.0


def test_donchian_rejects_short_series() -> None:
    with pytest.raises(ValueError, match="^OHLC series is shorter than period$"):
        DonchianChannels(4).calculate(
            _request(
                {
                    "high": [10.0, 12.0, 11.0],
                    "low": [8.0, 9.0, 9.0],
                    "close": [9.0, 11.0, 10.0],
                }
            )
        )


def test_bollinger_matches_sma_and_population_std_reference() -> None:
    output = BollingerBands(4, 2.0).calculate(_request({"close": [1.0, 2.0, 3.0, 4.0]}))
    assert output.values["middle"] == pytest.approx(2.5)
    assert output.values["upper"] == pytest.approx(4.73606797749979)
    assert output.values["lower"] == pytest.approx(0.2639320225002102)


def test_bollinger_rejects_empty_series() -> None:
    with pytest.raises(ValueError, match="^close series must not be empty$"):
        BollingerBands(3).calculate(_request({"close": []}))


def test_bollinger_rejects_period_longer_than_series() -> None:
    with pytest.raises(ValueError, match="^close series is shorter than period$"):
        BollingerBands(4).calculate(_request({"close": [1.0, 2.0, 3.0]}))


def test_bollinger_rejects_invalid_multiplier() -> None:
    with pytest.raises(ValueError, match="^multiplier must be positive and finite$"):
        BollingerBands(3, 0.0)
