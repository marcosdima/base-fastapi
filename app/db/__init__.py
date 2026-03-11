from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from sqlmodel import create_engine, SQLModel
from ..utils.settings import settings


def _build_db_url(raw_url: str) -> str:
    if raw_url.startswith('sqlite'):
        return raw_url

    # SQLAlchemy requires 'postgresql://' instead of 'postgres://'
    url = raw_url.replace('postgres://', 'postgresql://', 1)

    # Remove Supabase-specific params not recognized by psycopg2 (e.g. 'supa')
    parsed = urlparse(url)
    params = {k: v for k, v in parse_qs(parsed.query).items() if k != 'supa'}
    clean_query = urlencode({k: v[0] for k, v in params.items()})
    
    return urlunparse(parsed._replace(query=clean_query))


engine = create_engine(_build_db_url(settings.POSTGRES_URL), echo=True)


def create_db_and_tables():
    from ..models import User  # Import here to avoid circular imports
    SQLModel.metadata.create_all(engine)
