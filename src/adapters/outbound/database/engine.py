from collections.abc import AsyncGenerator

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.adapters.config import get_config


def get_engine() -> AsyncEngine | Engine:
    config = get_config()
    return create_async_engine(config.database_app_url, echo=False, future=True)


_engine = get_engine()
_session_maker = sessionmaker(
    _engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_maker() as async_session:
        yield async_session
