# CONTRIBUTING

## Development order

Contract → Domain → Persistence/Infrastructure → Engine → Strategy/Analysis → Application → Orchestrator/UI

Do not start implementation from Telegram or orchestration.

## Quality

Every new Python file has one primary responsibility and is compatible with Python 3.13+.

## GitHub source of truth

Changes become canonical only after they are committed to GitHub and merged into main.

## Verification

Never weaken, reorder, or bypass G01–G07 to obtain a green result. Claims must be tied to exact-SHA GitHub Actions evidence.

## Product boundaries

Strategy sensors describe market conditions. They do not independently emit final BUY/SELL decisions and do not own risk, cost, execution, or provider transport.
