from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.adapters.config import get_config

_engine: Optional[AsyncEngine] = None
_session_maker: Optional[sessionmaker] = None


def get_engine() -> AsyncEngine | Engine:
    global _engine
    if _engine is None:
        config = get_config()
        _engine = create_async_engine(config.database_app_url, echo=False, future=True)
    return _engine


def get_session_maker() -> sessionmaker:
    global _session_maker
    if _session_maker is None:
        engine = get_engine()
        _session_maker = sessionmaker(
            engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )
    return _session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = get_session_maker()
    async with session_maker() as async_session:
        yield async_session
