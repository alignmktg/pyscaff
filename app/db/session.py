"""Database session management and dependencies."""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

# Fix SQLite URL for async
if DATABASE_URL.startswith("sqlite"):
    if not DATABASE_URL.startswith("sqlite+aiosqlite"):
        DATABASE_URL = DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    future=True,
    pool_pre_ping=True,
    # SQLite-specific settings
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session.

    Yields:
        AsyncSession: Database session for the request

    Usage:
        @router.post("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # Use db session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()