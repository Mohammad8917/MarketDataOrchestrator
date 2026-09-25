"""FILE: tests/integration/test_indicator_sma_bb.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify Bollinger Bands consumes the canonical SimpleMovingAverage implementation.
LAYER: tests
OWNS: Integration coverage for SMA-to-Bollinger dependency wiring.
DOES_NOT_OWN: indicator algorithm implementation, registry ownership, release approval
DEPENDENCIES: indicators.core.base; indicators.trend.sma; indicators.volatility.bollinger_bands; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone

from indicators.core.base import IndicatorOutput, IndicatorRequest
from indicators.trend.sma import SimpleMovingAverage
from indicators.volatility.bollinger_bands import BollingerBands


def test_bollinger_middle_band_uses_existing_sma(monkeypatch) -> None:
    now = datetime(2026, 9, 24, 12, tzinfo=timezone.utc)
    request = IndicatorRequest(
        series={"close": [1.0, 2.0, 3.0]},
        event_time=now,
        received_at=now,
        source_event_id="evt-bb-sma",
    )

    calls = {"count": 0}

    def fake_calculate(self: SimpleMovingAverage, request: IndicatorRequest) -> IndicatorOutput:
        calls["count"] += 1
        return IndicatorOutput(
            values={"sma": 10.0},
            event_time=request.event_time,
            indicator_id="sma",
        )

    monkeypatch.setattr(SimpleMovingAverage, "calculate", fake_calculate)

    output = BollingerBands(3, 2.0).calculate(request)

    assert calls["count"] == 1
    assert output.values["middle"] == 10.0

    # Independent oracle:
    #   mean = 10, data = [1, 2, 3]
    #   variance = 194/3 (ddof=0, per evidence/INDICATOR_BATCH_DONCHIAN_BOLLINGER.json)
    #   sigma = sqrt(194/3) ≈ 8.04155872120988
    #   upper = 10 + 2*sigma ≈ 26.08311744241976
    #   lower = 10 - 2*sigma ≈ -6.083117442419759
    assert output.values["upper"] == 26.08311744241976
    assert output.values["lower"] == -6.083117442419759
