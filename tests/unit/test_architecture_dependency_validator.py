"""FILE: tests/unit/test_architecture_dependency_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Regression-test frozen cross-layer architecture dependency semantics.
LAYER: tests
OWNS: Regression assertions for same-layer allowance and forbidden cross-layer rejection semantics.
DOES_NOT_OWN: Architecture policy definition or validator implementation.
DEPENDENCIES: validation.architecture_dependency_validator, pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from validation.architecture_dependency_validator import (
    ALLOWED,
    FORBIDDEN,
    cross_layer_imports,
)


def test_same_layer_import_is_internal() -> None:
    imported = {"domain", "shared"}
    assert cross_layer_imports("domain", imported) == {"shared"}


def test_forbidden_domain_to_analysis_remains_forbidden() -> None:
    imported = cross_layer_imports("domain", {"domain", "analysis"})
    assert "analysis" in FORBIDDEN["domain"]
    assert "analysis" not in ALLOWED["domain"]
    assert imported == {"analysis"}


def test_same_layer_ingestion_is_not_an_architecture_edge() -> None:
    imported = cross_layer_imports("ingestion", {"ingestion"})
    assert imported == set()
