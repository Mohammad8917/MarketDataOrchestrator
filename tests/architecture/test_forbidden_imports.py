"""FILE: tests/architecture/test_forbidden_imports.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the frozen architecture policy has no contradictory allowed/forbidden layer edges.
LAYER: tests
OWNS: Architecture policy consistency regression coverage.
DOES_NOT_OWN: production architecture policy definition, runtime orchestration, provider behavior
DEPENDENCIES: validation
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from validation.architecture_dependency_validator import ALLOWED, FORBIDDEN


def test_allowed_and_forbidden_edges_are_disjoint() -> None:
    for layer, forbidden in FORBIDDEN.items():
        assert forbidden.isdisjoint(ALLOWED.get(layer, set())), layer
