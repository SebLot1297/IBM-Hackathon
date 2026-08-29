# Contributing to FinPay API

## Code Style

- Follow PEP 8. Run `flake8` before committing.
- Maximum line length: 88 characters (Black default).
- Use type hints on all public functions.
- No `print()` statements — use the `logging` module.

## Security Rules (MANDATORY)

1. **Every endpoint that modifies state MUST call `require_auth()` before any business logic.**
2. Authentication must be validated before the request body is parsed for sensitive fields.
3. Never log full token values — log only the first 8 characters followed by `...`.
4. Input validation must reject unknown/extra fields; do not pass `**kwargs` to DB layer.

## Testing

- Every new endpoint requires at minimum:
  - One test for the authenticated happy path
  - One test for the unauthenticated rejection (401)
  - One test for invalid input (400)
- Test files live in `tests/` and are named `test_<module>.py`.
- Use `pytest`. Coverage must not drop below 80%.

## Pull Request Guidelines

- PR title must start with one of: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- PR description must list **all files intentionally changed** and the reason.
- Do not bundle database migrations with feature changes unless the feature requires
  the schema. If it does, call it out explicitly in the description.
- Keep PRs focused. A PR that touches auth, payments, AND migrations at the same time
  is a red flag — split it.

## Versioning

We follow semantic versioning. Bump `config.py::APP_VERSION` in the same commit as
any API-breaking change.
