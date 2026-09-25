# ADR-TEST-ORACLE — Expected-value derivation in tests

**Status:** Accepted  
**Date:** 2026-09-25

## Context

Contract and integration tests can silently become unreliable when expected numeric values are entered as unexplained literals. The Bollinger/SMA integration test exposed this failure mode: two successive hard-coded expected-value sets had no documented derivation.

## Decision

Every non-trivial numeric expected value in a contract or integration test MUST have either an inline mathematical derivation tied to the governing contract/evidence, or a clearly identified and independently justified oracle. The expected value MUST NOT be copied from the implementation under test.

For indicator tests, the derivation MUST identify the relevant semantic choice when applicable, such as population versus sample standard deviation, and any material precision rule.

## Consequence

Tests become auditable and resistant to self-referential expected values. When a contract changes, the expected-value derivation exposes exactly which assertion must change. This rule does not require changing production implementation merely to satisfy a test.

## Evidence

This decision was applied to tests/integration/test_indicator_sma_bb.py after the provenance audit of commits 7d193c95, b62ee415, and b928b189, with the governing Bollinger semantics recorded in evidence/INDICATOR_BATCH_DONCHIAN_BOLLINGER.json.
