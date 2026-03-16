from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlmodel import SQLModel, create_engine

from ..utils.settings import settings


def _build_db_url(raw_url: str) -> str:
    if raw_url.startswith('sqlite'):
        return raw_url

    # SQLAlchemy requires 'postgresql://' instead of 'postgres://'.
    url = raw_url.replace('postgres://', 'postgresql://', 1)

    # Remove Supabase-specific params not recognized by psycopg2 (e.g. 'supa').
    parsed = urlparse(url)
    params = {k: v for k, v in parse_qs(parsed.query).items() if k != 'supa'}
    clean_query = urlencode({k: v[0] for k, v in params.items()})

    return urlunparse(parsed._replace(query=clean_query))


engine = create_engine(_build_db_url(settings.POSTGRES_URL), echo=False)


def create_db_and_tables() -> None:
    from ..models import Permission, PermissionRole, Role, User, UserRole  # Import here to avoid circular imports.

    SQLModel.metadata.create_all(engine)
