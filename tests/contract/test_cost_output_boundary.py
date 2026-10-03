"""Adversarial contract tests for transaction-cost output boundaries."""

from datetime import datetime, timezone

import pytest

from shared.contracts.cost import CostOutput


@pytest.mark.parametrize("value", [0, 1, 0.0, 1.0, "true", None])
def test_cost_output_rejects_non_boolean_approved(value: object) -> None:
    with pytest.raises(ValueError, match="approved must be a boolean"):
        CostOutput(
            approved=value,  # type: ignore[arg-type]
            total_cost_fraction=0.1,
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            cost_id="cost-1",
        )


@pytest.mark.parametrize("version", ["", "   ", "\\t", "\\n"])
def test_cost_output_rejects_blank_contract_version(version: str) -> None:
    with pytest.raises(ValueError, match="contract_version must not be empty"):
        CostOutput(
            approved=True,
            total_cost_fraction=0.1,
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            cost_id="cost-1",
            contract_version=version,
        )
