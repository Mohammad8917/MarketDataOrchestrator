"""FILE: app/dependency_container.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Construct the application service from an injected evaluator dependency.
LAYER: app
OWNS: Dependency construction only.
DOES_NOT_OWN: analytical methodology, boundary-specific contracts, business decisions, risk allocation, execution, persistence, or delivery.
DEPENDENCIES: app.application, shared.contracts.opportunity_selection
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from collections.abc import Callable
from typing import TypeVar

from shared.contracts.opportunity_selection import OpportunitySelectionOutput

from app.application import OpportunityApplication

T = TypeVar("T")


def build_opportunity_application(
    evaluator: Callable[[T, int], OpportunitySelectionOutput],
) -> OpportunityApplication[T]:
    """Build the application service without selecting a concrete analytical layer."""
    return OpportunityApplication(evaluator)
