from __future__ import annotations

import json
from pathlib import Path

from validation.consumer_matrix_validator import validate


INVENTORY = """from indicators.core.base import IndicatorRequest, IndicatorOutput
FROZEN_CONTRACT_TYPES = (IndicatorRequest, IndicatorOutput)
"""


def _write_matrix(path: Path, contracts: list[str]) -> None:
    path.write_text(
        json.dumps({"contracts": [{"contract": item} for item in contracts]}), encoding="utf-8"
    )


def test_consumer_matrix_matches_frozen_inventory(tmp_path: Path) -> None:
    inventory = tmp_path / "inventory.py"
    matrix = tmp_path / "matrix.json"
    inventory.write_text(INVENTORY, encoding="utf-8")
    _write_matrix(
        matrix,
        [
            "indicators.core.base.IndicatorRequest",
            "indicators.core.base.IndicatorOutput",
        ],
    )
    assert validate(inventory, matrix) == []


def test_new_frozen_contract_without_matrix_entry_fails(tmp_path: Path) -> None:
    inventory = tmp_path / "inventory.py"
    matrix = tmp_path / "matrix.json"
    inventory.write_text(
        INVENTORY.replace(
            "FROZEN_CONTRACT_TYPES = (IndicatorRequest, IndicatorOutput)",
            "FROZEN_CONTRACT_TYPES = (IndicatorRequest, IndicatorOutput, NewContract)",
        ).replace(
            "from indicators.core.base import IndicatorRequest, IndicatorOutput",
            "from indicators.core.base import IndicatorRequest, IndicatorOutput, NewContract",
        ),
        encoding="utf-8",
    )
    _write_matrix(
        matrix, ["indicators.core.base.IndicatorRequest", "indicators.core.base.IndicatorOutput"]
    )
    findings = validate(inventory, matrix)
    assert findings == [
        "frozen contracts missing from consumer matrix: indicators.core.base.NewContract"
    ]
