# Test Count History Audit — 598 → 531

- **Audit date:** 2026-10-01
- **Repository:** Mohammad8917/MarketDataOrchestrator
- **Canonical branch checked:** main
- **Purpose:** Determine whether the reported 598 → 531 test-count change is a deletion, merge/deduplication, migration, or a scope/command difference.

## Result

The canonical GitHub history does **not** contain a verified 598 → 531 transition.

The verified sequence around the relevant development window is:

| Reference | CI workflow | Full pytest result |
|---|---|---:|
| PR #72 head `7ac5032` | Compliance CI #36832246394 / G05 | **598 passed** |
| PR #73 head `019054a` | Compliance CI #36835368145 / G05 | **598 passed** |
| PR #74 head `a1f433a` | Compliance CI #36839441859 / G05 | **598 passed** |
| PR #75 head `b36309a` | Compliance CI #36902896659 / G05 | **609 passed** |
| PR #76 head `3840478` | Compliance CI #36905084211 / G05 | **623 passed** |
| PR #77 head `3b202a8` | Compliance CI #36905674319 / G05 | **636 passed** |
| PR #78 head `76b654e` | Compliance CI #36906833562 / G05 | **640 passed** |
| PR #81 head `626eaa2` | Compliance CI #36911980267 / G05 | **651 passed** |

Therefore:

- **598 is machine-verified** in the canonical CI history.
- **531 is not machine-verified** in the canonical GitHub CI history examined.
- No canonical 67-test deletion has been established.
- The observed canonical direction after 598 is an **increase**, not a decrease: 598 → 609 → 623 → 636 → 640 → 651.
- Consequently, it is incorrect to document the 598 → 531 change as a test deletion/refactor until the source of the 531 figure is identified.

## Important distinction

The G03 Unit/Contract workflow is a different test scope from G05 full coverage.

For example:

- PR #74 G03: **484 passed**
- PR #75 G03: **495 passed**

G05 executes the repository-wide `pytest -q` command and is the authoritative source for the full-suite counts above.

A count from a different local command, directory selection, branch, or test discovery configuration can therefore differ from the G05 full-suite count without implying test deletion.

## Current audit conclusion

**Status: NOT A VERIFIED DELETION.**

The 598 → 531 claim remains **unresolved / source-dependent**. The next evidence required is the exact command, branch/SHA, and pytest output that produced 531.

Until that source is identified, no tests should be restored, deleted, merged, or reclassified solely to make the count return to 598.

## Architectural implication

This audit does not change the Backtest/Composition Replay architecture and does not justify any contract change.

The existing decision remains:

- Backtest evolves through the canonical `BacktestReplayEngine`.
- Composition Replay is complementary to Signal/Strategy; it does not replace them.
- `SignalComposer` remains the composition interface.
- `CompositionReplayOutput` remains the replay output boundary.

## Evidence links

- PR #72: https://github.com/Mohammad8917/MarketDataOrchestrator/pull/72
- PR #73: https://github.com/Mohammad8917/MarketDataOrchestrator/pull/73
- PR #74: https://github.com/Mohammad8917/MarketDataOrchestrator/pull/74
- PR #75: https://github.com/Mohammad8917/MarketDataOrchestrator/pull/75
- PR #76: https://github.com/Mohammad8917/MarketDataOrchestrator/pull/76
- PR #77: https://github.com/Mohammad8917/MarketDataOrchestrator/pull/77
- PR #78: https://github.com/Mohammad8917/MarketDataOrchestrator/pull/78
- PR #81: https://github.com/Mohammad8917/MarketDataOrchestrator/pull/81
- Compliance CI #36832246394: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36832246394
- Compliance CI #36839441859: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36839441859
- Compliance CI #36902896659: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36902896659
- Compliance CI #36911980267: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36911980267
