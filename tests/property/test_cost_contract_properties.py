from datetime import datetime, timezone

from hypothesis import given, settings, strategies as st

from shared.contracts.cost import CostOutput, CostRequest


@settings(database=None, derandomize=True)
@given(
    spread=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    slippage=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    fee=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    maximum=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
)
def test_cost_request_accepts_bounded_finite_fractions(
    spread: float, slippage: float, fee: float, maximum: float
) -> None:
    event_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    request = CostRequest(
        spread_fraction=spread,
        slippage_fraction=slippage,
        fee_fraction=fee,
        max_cost_fraction=maximum,
        event_time=event_time,
        received_at=event_time,
        source_event_id="event-1",
    )
    assert 0 <= request.spread_fraction <= 1
    assert 0 <= request.slippage_fraction <= 1
    assert 0 <= request.fee_fraction <= 1
    assert 0 <= request.max_cost_fraction <= 1


@settings(database=None, derandomize=True)
@given(total=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False))
def test_cost_output_preserves_finite_bounded_total(total: float) -> None:
    output = CostOutput(
        approved=total <= 0.5,
        total_cost_fraction=total,
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        cost_id="cost-1",
    )
    assert 0 <= output.total_cost_fraction <= 1
