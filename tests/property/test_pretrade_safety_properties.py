from datetime import datetime, timezone

from hypothesis import given, settings, strategies as st

from shared.contracts.pretrade_safety import PreTradeSafetyOutput


@settings(database=None, derandomize=True)
@given(
    action=st.sampled_from(("BUY", "SELL")),
    exposure=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
)
def test_approved_pretrade_output_is_trade_action_without_reasons(
    action: str, exposure: float
) -> None:
    output = PreTradeSafetyOutput(
        approved=True,
        action=action,
        exposure_fraction=exposure,
        reasons=(),
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        safety_id="safety-1",
    )
    assert output.approved
    assert output.action in {"BUY", "SELL"}
    assert output.reasons == ()


@settings(database=None, derandomize=True)
@given(
    reason=st.sampled_from(
        ("COST_REJECTED", "LIQUIDITY_REJECTED", "RISK_REJECTED", "DECISION_WAIT")
    ),
    exposure=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
)
def test_rejected_pretrade_output_is_no_trade_with_reason(
    reason: str, exposure: float
) -> None:
    output = PreTradeSafetyOutput(
        approved=False,
        action="NO_TRADE",
        exposure_fraction=exposure,
        reasons=(reason,),
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        safety_id="safety-1",
    )
    assert not output.approved
    assert output.action == "NO_TRADE"
    assert output.reasons == (reason,)
