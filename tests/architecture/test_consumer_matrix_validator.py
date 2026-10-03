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


def test_frozen_inventory_supports_annassign_and_import_alias(tmp_path: Path) -> None:
    from validation.consumer_matrix_validator import frozen_contract_types

    inventory = tmp_path / "inventory.py"
    inventory.write_text(
        "from indicators.core.base import IndicatorRequest as Request\n"
        "FROZEN_CONTRACT_TYPES: tuple = (Request,)\n",
        encoding="utf-8",
    )
    assert frozen_contract_types(inventory) == ["indicators.core.base.IndicatorRequest"]


def test_frozen_inventory_rejects_star_import_entry(tmp_path: Path) -> None:
    from validation.consumer_matrix_validator import frozen_contract_types

    inventory = tmp_path / "inventory.py"
    inventory.write_text(
        "from indicators.core.base import *\n"
        "FROZEN_CONTRACT_TYPES = (IndicatorRequest,)\n",
        encoding="utf-8",
    )
    import pytest
    with pytest.raises(ValueError, match="unresolved entry"):
        frozen_contract_types(inventory)


def test_frozen_inventory_rejects_missing_declaration(tmp_path: Path) -> None:
    from validation.consumer_matrix_validator import frozen_contract_types

    inventory = tmp_path / "inventory.py"
    inventory.write_text("VALUE = ()\n", encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="declaration not found"):
        frozen_contract_types(inventory)


def test_frozen_inventory_rejects_non_sequence(tmp_path: Path) -> None:
    from validation.consumer_matrix_validator import frozen_contract_types

    inventory = tmp_path / "inventory.py"
    inventory.write_text(
        "from indicators.core.base import IndicatorRequest\n"
        "FROZEN_CONTRACT_TYPES = IndicatorRequest\n",
        encoding="utf-8",
    )
    import pytest
    with pytest.raises(ValueError, match="must be a tuple/list"):
        frozen_contract_types(inventory)


def test_matrix_rejects_non_list_contracts(tmp_path: Path) -> None:
    from validation.consumer_matrix_validator import matrix_contract_types

    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps({"contracts": {}}), encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="must be a list"):
        matrix_contract_types(matrix)


def test_matrix_rejects_malformed_entry(tmp_path: Path) -> None:
    from validation.consumer_matrix_validator import matrix_contract_types

    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps({"contracts": [{"contract": 1}]}), encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="string contract"):
        matrix_contract_types(matrix)


def test_validate_rejects_duplicates_and_stale_contracts(tmp_path: Path) -> None:
    inventory = tmp_path / "inventory.py"
    matrix = tmp_path / "matrix.json"
    inventory.write_text(INVENTORY, encoding="utf-8")
    _write_matrix(
        matrix,
        [
            "indicators.core.base.IndicatorRequest",
            "indicators.core.base.IndicatorRequest",
            "stale.Contract",
        ],
    )
    findings = validate(inventory, matrix)
    assert findings == [
        "duplicate consumer-matrix contracts: indicators.core.base.IndicatorRequest",
        "frozen contracts missing from consumer matrix: indicators.core.base.IndicatorOutput",
        "consumer matrix contains non-frozen/stale contracts: stale.Contract",
    ]


def test_frozen_inventory_rejects_unresolved_name(tmp_path: Path) -> None:
    from validation.consumer_matrix_validator import frozen_contract_types
    import pytest

    inventory = tmp_path / "inventory.py"
    inventory.write_text(
        "FROZEN_CONTRACT_TYPES = (UnknownContract,)\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unresolved entry"):
        frozen_contract_types(inventory)
