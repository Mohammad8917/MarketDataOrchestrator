"""FILE: app/dependency_container.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Wire application dependencies for the canonical opportunity orchestration boundary.
LAYER: app
OWNS: Dependency construction only.
DOES_NOT_OWN: analytical methodology, business decisions, risk allocation, execution, persistence, or delivery.
DEPENDENCIES: app.application, composition.opportunity_chain_pipeline
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from app.application import OpportunityApplication
from composition.opportunity_chain_pipeline import ComposedOpportunityChainPipeline


def build_opportunity_application() -> OpportunityApplication:
    """Build the application service with canonical composition dependencies."""
    return OpportunityApplication(ComposedOpportunityChainPipeline())
