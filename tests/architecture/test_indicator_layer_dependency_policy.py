"""FILE: tests/architecture/test_indicator_layer_dependency_policy.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Guard the indicator-layer internal dependency policy against regression.
LAYER: tests
OWNS: Architecture regression checks for indicator internal dependencies.
DOES_NOT_OWN: Production dependency validation implementation or business behavior.
DEPENDENCIES: validation.architecture_dependency_validator; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from validation.architecture_dependency_validator import dependency_allowed


def test_indicators_can_import_each_other() -> None:
    assert dependency_allowed("indicators", "indicators")


def test_indicators_cannot_import_strategy() -> None:
    assert not dependency_allowed("indicators", "strategy")
