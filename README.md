# FastAPI Base Starter

Production-oriented starting point for FastAPI projects with:

- SQLModel + SQLAlchemy
- Alembic migrations
- JWT-like token auth (HMAC SHA-256)
- Role and permission authorization
- Test suite with pytest

This repository is intentionally opinionated, so you can clone it and focus on business features instead of repeating boilerplate.

## What This Template Gives You

- Clean app structure (`models`, `services`, `routes`, `db`, `utils`)
- Environment-based settings with `pydantic-settings`
- Startup wiring through FastAPI lifespan
- Permission checks at route level
- Ready-to-run migration history (schema + seeded role/permissions)

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create `.env` in project root:

```env
SECRET_KEY="change-me"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
POSTGRES_URL="postgresql://user:password@localhost:5432/dbname"
```

### 3. Run API in development

```bash
source .venv/bin/activate
fastapi dev app/main.py
```

### 4. Run tests

```bash
pytest
```

## Project Layout

```text
app/
	main.py                  # FastAPI app + lifespan startup/shutdown
	db/
		db.py                  # Engine creation + DB URL normalization
		migrations/            # Alembic environment and revisions
	models/                  # SQLModel entities
	routes/                  # HTTP endpoints
	services/                # Business logic
	utils/
		settings.py            # Environment settings
		enums.py               # Permission enum source of truth
tests/                     # Pytest suite
```

## Important Files To Customize First

### `app/utils/settings.py`

This is where all required `.env` fields are declared through `Settings`.

- Add new config fields here when your project grows.
- Keep the types strict (`str`, `int`, etc.) so invalid configuration fails fast.
- `.env` loading is defined via:

```python
model_config = SettingsConfigDict(env_file='.env')
```

If you forget to define a required field in `.env`, app startup fails early with a clear validation error.

### `app/utils/enums.py` (`PermissionName`)

`PermissionName` is the source of truth for authorization permission names.

- Add new permission constants here first.
- Reuse enum values in routes/services to avoid string typos.
- Keep naming stable because migrations and DB rows depend on these values.

### `app/db/migrations/versions/3c14bd9ff3ba_seed_admin_role_and_permissions.py`

This migration seeds:

- Permission rows
- The `ADMIN` role
- Role-to-permission links

It imports `PermissionName` from `app.utils`, so enum updates should be reflected in migration data strategy.

When you introduce new permissions:

1. Add value to `PermissionName` in `app/utils/enums.py`.
2. Create a new Alembic migration to insert that permission and update role mappings.
3. Update route checks where needed.

## Auth and Authorization Flow

- Token creation and validation are implemented in `app/routes/dependencies/auth.py`.
- Permission checks are enforced in routes like `app/routes/roles.py`.
- Role/permission lookup logic is centralized in `app/services/roles_service.py`.

## Database and Migrations

### Apply migrations

```bash
source .venv/bin/activate
alembic -c app/db/alembic.ini upgrade head
```

### Create a new migration

```bash
source .venv/bin/activate
alembic -c app/db/alembic.ini revision --autogenerate -m "describe change"
```

Notes:

- Alembic env (`app/db/migrations/env.py`) loads `.env` and uses `POSTGRES_URL`.
- `app/db/db.py` normalizes `postgres://` to `postgresql://` and strips unsupported query params.

## How To Extend This Base

1. Add or modify models in `app/models`.
2. Add service methods in `app/services`.
3. Expose endpoints in `app/routes`.
4. Protect endpoints with permission checks.
5. Create migration(s) for schema/data changes.
6. Add tests before merging.

## Testing Notes

- The test suite is configured to isolate DB state per test.
- Prefer creating explicit helpers for repetitive test setup.
- Keep permission-related tests in `tests/roles` so regression scope stays clear.

## Suggested Next Improvements

- Add Docker and docker-compose for local infrastructure.
- Add CI pipeline (`pytest` + migration checks).
- Replace custom token implementation with a dedicated JWT library if required by your security standards.