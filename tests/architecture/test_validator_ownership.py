"""FILE: tests/architecture/test_validator_ownership.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the architecture dependency validator's real same-layer and upward-dependency rules.
LAYER: tests
OWNS: Behavior guards for the canonical architecture dependency policy.
DOES_NOT_OWN: production code depending on tests, runtime orchestration, release approval
DEPENDENCIES: validation.architecture_dependency_validator; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from validation.architecture_dependency_validator import dependency_allowed


def test_indicators_can_import_each_other() -> None:
    assert dependency_allowed("indicators", "indicators") is True


def test_indicators_cannot_import_analysis() -> None:
    assert dependency_allowed("indicators", "analysis") is False


def test_indicators_cannot_import_strategy() -> None:
    assert dependency_allowed("indicators", "strategy") is False
