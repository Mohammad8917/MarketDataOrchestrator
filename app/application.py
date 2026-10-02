"""FILE: app/application.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Orchestrate an injected opportunity evaluator at application boundary.
LAYER: app
OWNS: Lifecycle invocation and dependency delegation only.
DOES_NOT_OWN: analytical methodology, boundary-specific contracts, safety approval, ranking, selection, risk allocation, execution, persistence, or delivery.
DEPENDENCIES: app.application_contract, shared.contracts.opportunity_selection
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from collections.abc import Callable
from typing import Generic, TypeVar

from shared.contracts.opportunity_selection import OpportunitySelectionOutput

from app.application_contract import ApplicationRequest

T = TypeVar("T")


class OpportunityApplication(Generic[T]):
    """Invoke an injected evaluator without owning analytical behavior."""

    def __init__(
        self, evaluator: Callable[[T, int], OpportunitySelectionOutput]
    ) -> None:
        self._evaluator = evaluator

    def run(self, request: ApplicationRequest[T]) -> OpportunitySelectionOutput:
        """Delegate one immutable application request and preserve upstream errors."""
        return self._evaluator(request.payload, request.limit)
