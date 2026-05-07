from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from core.config import get_settings
from db.models import Base


def _build_async_database_url(database_url: str) -> tuple[str, dict[str, object]]:
    """Normalize a Neon Postgres URL for SQLAlchemy's asyncpg dialect.

    Neon connection strings are commonly emitted as postgresql:// URLs with
    sslmode=require. SQLAlchemy's async engine needs the asyncpg driver prefix,
    and asyncpg receives TLS configuration through connect_args.
    """

    parsed = urlsplit(database_url)
    scheme = parsed.scheme

    if scheme in {"postgres", "postgresql"}:
        scheme = "postgresql+asyncpg"
    elif scheme != "postgresql+asyncpg":
        raise ValueError(
            "DATABASE_URL must use postgres, postgresql, or postgresql+asyncpg scheme"
        )

    raw_query_items = dict(parse_qsl(parsed.query, keep_blank_values=True))
    sslmode = raw_query_items.pop("sslmode", None)

    # Neon URLs can include libpq-only options (for psycopg/psql), e.g.
    # `channel_binding=require`. asyncpg doesn't accept these as connect kwargs.
    # Keep only SQLAlchemy asyncpg-dialect-safe query options.
    query_items: dict[str, str] = {}
    if "prepared_statement_cache_size" in raw_query_items:
        query_items["prepared_statement_cache_size"] = raw_query_items[
            "prepared_statement_cache_size"
        ]

    # Disable asyncpg's prepared statement cache for PgBouncer-compatible Neon
    # pooled URLs. It is harmless for direct Neon URLs and avoids transaction
    # pooler statement reuse issues.
    query_items.setdefault("prepared_statement_cache_size", "0")

    normalized_url = urlunsplit(
        (
            scheme,
            parsed.netloc,
            parsed.path,
            urlencode(query_items),
            parsed.fragment,
        )
    )

    connect_args: dict[str, object] = {}
    if sslmode in {"require", "prefer", "verify-ca", "verify-full"}:
        connect_args["ssl"] = True

    return normalized_url, connect_args


settings = get_settings()
DATABASE_URL, CONNECT_ARGS = _build_async_database_url(settings.database_url)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args=CONNECT_ARGS,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a transactional async DB session."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    if not settings.auto_create_schema:
        return

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
