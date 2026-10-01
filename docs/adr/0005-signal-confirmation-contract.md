# ADR 0005 — Signal Confirmation Contract

- Status: Accepted
- Date: 2026-10-01
- Architecture: Frozen v1.0

## Decision

Introduce `signal_confirmation_boundary` version `1.0.0` as the executable contract for analytical confirmation.

The boundary accepts finite analytical evidence values and returns a bounded confirmation score plus a boolean confirmation state. Inputs and outputs are immutable value objects with UTC provenance.

## Scope

The contract is market-agnostic and applies equally to Crypto, Forex, and Gold.

It does not define:
- signal generation;
- confirmation methodology;
- market/provider access;
- persistence;
- cost or liquidity assessment;
- risk;
- decision finalization;
- trading actions.

Those concerns remain separate contracts or future methodologies.

## Consequence

Confirmation implementations must be introduced only after this contract and its strong tests pass. Existing confirmation skeletons remain frozen until an explicit methodology is defined and verified.

## Registry reconciliation

| contract_id | reason |
|---|---|
| signal_confirmation_boundary | SignalConfirmation is a behavioral runtime protocol; ConfirmationRequest and ConfirmationOutput are frozen value contracts |
