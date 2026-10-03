from datetime import datetime, timezone

from hypothesis import given, settings, strategies as st

from shared.contracts.liquidity import LiquidityRequest


@settings(database=None, derandomize=True)
@given(
    available=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    required=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    requested=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    maximum=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
)
def test_liquidity_request_accepts_bounded_finite_fractions(
    available: float, required: float, requested: float, maximum: float
) -> None:
    event_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    request = LiquidityRequest(
        available_depth_fraction=available,
        required_depth_fraction=required,
        requested_participation_fraction=requested,
        max_participation_fraction=maximum,
        event_time=event_time,
        received_at=event_time,
        source_event_id="event-1",
    )
    assert 0 <= request.available_depth_fraction <= 1
    assert 0 <= request.required_depth_fraction <= 1
    assert 0 <= request.requested_participation_fraction <= 1
    assert 0 <= request.max_participation_fraction <= 1
