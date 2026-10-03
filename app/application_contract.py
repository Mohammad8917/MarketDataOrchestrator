"""FILE: app/application_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the typed application request envelope for opportunity orchestration.
LAYER: app
OWNS: Immutable lifecycle request envelope and local limit invariant only.
DOES_NOT_OWN: analytical methodology, boundary-specific contracts, safety approval, risk allocation, execution, persistence, or delivery.
DEPENDENCIES: None declared in current implementation.
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ApplicationRequest(Generic[T]):
    """Immutable application envelope around an externally assembled analytical request."""

    payload: T
    limit: int

    def __post_init__(self) -> None:
        if self.payload is None:
            raise ValueError("payload must not be None")
        if type(self.limit) is not int:
            raise TypeError("limit must be an int")
        if self.limit < 1:
            raise ValueError("limit must be at least 1")
