# ADR-0027 — Bandit Suppression Policy

**Status:** Accepted  
**Date:** 2026-09-25  
**Scope:** G06 Security / Supply Chain  
**Related:** ADR-0013, ADR-0025, ADR-0026

## Context

G06 uses Bandit in fail-closed mode. The state-generation utility contains fixed-argument Git subprocess calls that do not use a shell and do not accept user-controlled command input. Bandit reports B404/B603 for the subprocess mechanism even though the concrete invocation is constrained.

Bandit also reported B105 for the literal `"OK"` label. That finding is removed by substituting the semantically equivalent `"PASS"` label; no suppression is used for B105.

## Decision

1. **Suppression requires an explanatory comment.** Every Bandit suppression must identify the rule and explain the concrete security reason the finding is a false positive.
2. **Substitution is preferred.** When a finding can be removed by a semantically equivalent code change without weakening behavior, substitution must be used instead of suppression.
3. **Scope is limited to utility scripts.** This suppression policy does not authorize suppressions in production domain, persistence, backtest, indicator, validation, or other core runtime code.
4. **Every suppression is reviewable.** A suppression must be examined during code review for command construction, shell usage, input provenance, and whether a safer implementation is reasonably available.
5. **Fail-closed remains mandatory.** Suppression does not disable G06 or reduce its gate requirement. Any new or unrelated Bandit finding remains a G06 failure.

## Applied Case

For `scripts/generate_state.py`:
- B105 is resolved by changing the generated PASS label from `OK` to `PASS`.
- B404 is suppressed with an inline rationale because the utility invokes fixed Git commands without user input.
- B603 is suppressed with an inline rationale because the command is passed as an argument list and shell execution is not enabled.
- The existing exception handling remains unchanged.

## Consequence

The security gate continues to execute normally. The suppression records the reviewed security boundary rather than hiding an unresolved finding. Future changes to the command construction or input provenance require a fresh review of the suppression.
