# CONTRIBUTING

## Development order

Contract → Domain → Persistence / Infrastructure → Engine → Strategy / Analysis → Application → Orchestrator / UI

Do not start from Telegram or orchestration.

## Quality

- Python 3.13+
- One Python file = one primary responsibility.
- Strong focused tests before expanding the next dependency.
- Exact-SHA GitHub Actions evidence is required for gate claims.

## GitHub source of truth

Only work committed to GitHub and merged into main is canonical.

## Compliance

Never weaken, reorder, or bypass G01–G07 to obtain a green result.

## Product boundaries

Strategy sensors do not independently own final trading decisions. Risk, cost, execution, provider I/O, and persistence remain separate boundaries.
