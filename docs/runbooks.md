# FILE: docs/runbooks.md
# KIT: Architecture & Implementation Compliance Kit
# FILE_VERSION: 1.0.0
# DATE_GREGORIAN: 2026-09-24
# DATE_PERSIAN: 1405-07-02
# AUTHOR: محمد حسن زاده
# RESPONSIBILITY: Define operational response procedures required by the compliance kit.
# LAYER: operations
# OWNS: Provider outage, rate-limit, credential, data-corruption, clock-skew, queue-saturation, contract-incompatibility, and failed-deployment response procedures.
# DOES_NOT_OWN: Automated incident execution, provider implementation, credential storage, or release approval.
# DEPENDENCIES: N/A
# PYTHON: N/A
# LICENSE: Proprietary — All Rights Reserved
# NOTICE: Unauthorized use prohibited without written authorization
# COMPLIANCE: Architecture & Implementation Compliance Kit v1.0

# Operational Runbooks

## Provider outage
1. Stop new work for the affected provider when error budgets or health checks cross the declared threshold.
2. Preserve the last known provider identity, request correlation ID, event time, and failure evidence.
3. Prevent provider failure from propagating into unrelated providers.
4. Resume only after health checks and contract validation recover.

## Rate limit
1. Honor provider-declared retry-after information when available.
2. Apply bounded exponential backoff with jitter and a hard retry ceiling.
3. Do not retry non-idempotent mutations without an explicit idempotency key.
4. Record rate-limit evidence without logging credentials.

## Credential incident
1. Disable the affected credential immediately.
2. Rotate/revoke it through the approved secret-management path.
3. Verify that no credential value entered logs, telemetry, fixtures, URLs, or serialized state.
4. Re-run secret and security gates before restoration.

## Data corruption
1. Stop propagation of suspect data.
2. Preserve immutable source-event identifiers and content digests.
3. Restore from the last verified durable checkpoint when available.
4. Reconcile replayed events and record the recovery evidence.

## Clock skew
1. Detect provider/local clock skew against the declared threshold.
2. Mark the affected path degraded or fail-closed according to the temporal contract.
3. Never fabricate provider event timestamps.
4. Reconcile only after clock synchronization is observable and within threshold.

## Queue saturation
1. Apply bounded queue/resource limits.
2. Stop or shed non-critical work before memory or latency budgets are exhausted.
3. Preserve ordering and durable acknowledgements for state-changing work.
4. Resume only after queue depth and processing latency return below thresholds.

## Contract incompatibility
1. Reject incompatible payloads at the contract boundary.
2. Preserve the source event and contract/version evidence.
3. Do not silently coerce incompatible provider semantics.
4. Roll back or deploy a compatibility adapter through the approved change process.

## Failed deployment
1. Stop further promotion.
2. Preserve source commit, build fingerprint, test/security evidence, and deployment logs.
3. Roll back to the last verified artifact when rollback criteria are met.
4. Re-run the full applicable release gates before retrying.
