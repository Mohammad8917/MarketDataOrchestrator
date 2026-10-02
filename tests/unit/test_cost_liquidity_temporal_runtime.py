from datetime import datetime, timezone

import pytest

from shared.contracts.cost import CostOutput, CostRequest
from shared.contracts.liquidity import LiquidityOutput, LiquidityRequest


UTC = timezone.utc
EVENT_TIME = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize("event_time", ["2026-01-01T00:00:00Z", 0, None])
def test_cost_request_rejects_invalid_event_time_runtime_types(event_time: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        CostRequest(
            spread_fraction=0.01,
            slippage_fraction=0.01,
            fee_fraction=0.01,
            max_cost_fraction=0.10,
            event_time=event_time,  # type: ignore[arg-type]
            received_at=EVENT_TIME,
            source_event_id="event-1",
        )


@pytest.mark.parametrize("received_at", ["2026-01-01T00:00:00Z", 0, None])
def test_cost_request_rejects_invalid_received_at_runtime_types(received_at: object) -> None:
    with pytest.raises(ValueError, match="received_at must be a datetime"):
        CostRequest(
            spread_fraction=0.01,
            slippage_fraction=0.01,
            fee_fraction=0.01,
            max_cost_fraction=0.10,
            event_time=EVENT_TIME,
            received_at=received_at,  # type: ignore[arg-type]
            source_event_id="event-1",
        )


@pytest.mark.parametrize("event_time", ["2026-01-01T00:00:00Z", 0, None])
def test_cost_output_rejects_invalid_event_time_runtime_types(event_time: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        CostOutput(
            approved=True,
            total_cost_fraction=0.05,
            event_time=event_time,  # type: ignore[arg-type]
            cost_id="cost-1",
        )


@pytest.mark.parametrize("event_time", ["2026-01-01T00:00:00Z", 0, None])
def test_liquidity_request_rejects_invalid_event_time_runtime_types(
    event_time: object,
) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        LiquidityRequest(
            available_depth_fraction=0.50,
            required_depth_fraction=0.25,
            requested_participation_fraction=0.10,
            max_participation_fraction=0.20,
            event_time=event_time,  # type: ignore[arg-type]
            received_at=EVENT_TIME,
            source_event_id="event-1",
        )


@pytest.mark.parametrize("received_at", ["2026-01-01T00:00:00Z", 0, None])
def test_liquidity_request_rejects_invalid_received_at_runtime_types(
    received_at: object,
) -> None:
    with pytest.raises(ValueError, match="received_at must be a datetime"):
        LiquidityRequest(
            available_depth_fraction=0.50,
            required_depth_fraction=0.25,
            requested_participation_fraction=0.10,
            max_participation_fraction=0.20,
            event_time=EVENT_TIME,
            received_at=received_at,  # type: ignore[arg-type]
            source_event_id="event-1",
        )


@pytest.mark.parametrize("event_time", ["2026-01-01T00:00:00Z", 0, None])
def test_liquidity_output_rejects_invalid_event_time_runtime_types(
    event_time: object,
) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        LiquidityOutput(
            approved=True,
            event_time=event_time,  # type: ignore[arg-type]
            liquidity_id="liquidity-1",
        )
