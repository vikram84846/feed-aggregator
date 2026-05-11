"""
Async database configuration and session management.

This module:
- Creates the SQLAlchemy async engine
- Configures the async session factory
- Provides a reusable database session dependency

"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import get_settings

# Load application settings
settings = get_settings()


# Create asynchronous database engine
async_engine = create_async_engine(
    url=settings.DB_URL,
    echo=True if settings.ENV.lower() == "dev" else False,
    pool_pre_ping=True,
)


# Async session factory
AsyncLocalSession = async_sessionmaker(async_engine, autoflush=True, autocommit=False)


async def get_async_session():
    """
    Provide an asynchronous database session.

    Yields:
        AsyncSession: Active SQLAlchemy async session.

    Notes:
        - Session is automatically closed after request completion.

    Example:
        async def route(
            db: AsyncSession = Depends(get_async_session)
        ):
            ...
    """
    async with AsyncLocalSession() as session:
        yield session
