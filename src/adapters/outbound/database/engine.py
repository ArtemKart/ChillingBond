from collections.abc import AsyncGenerator
from typing import Optional
import time
import logging

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.adapters.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_engine: Optional[AsyncEngine] = None
_session_maker: Optional[sessionmaker] = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        config = get_config()
        _engine = create_async_engine(
            config.database_app_url,
            echo=True,
            future=True,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=1800,
        )
        _setup_query_logging(_engine)

    return _engine


def _setup_query_logging(engine: AsyncEngine) -> None:
    """Настраивает логирование времени выполнения SQL запросов"""
    sync_engine = engine.sync_engine

    @event.listens_for(sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())

        query_preview = statement.replace('\n', ' ')[:200]
        logger.info(f"🔵 Starting query: {query_preview}...")

    @event.listens_for(sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        query_preview = statement.replace('\n', ' ')[:200]


        if total > 1.0:
            logger.warning(f"🔴 SLOW QUERY ({total:.4f}s): {query_preview}...")
        elif total > 0.5:
            logger.warning(f"🟡 Query took {total:.4f}s: {query_preview}...")
        else:
            logger.info(f"✅ Query completed in {total:.4f}s")


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

    session_start = time.time()
    logger.info("🔌 Creating DB session...")

    async with session_maker() as async_session:
        session_created = time.time() - session_start
        logger.info(f"✅ DB session created in {session_created:.4f}s")

        yield async_session

        logger.info("🔌 Closing DB session...")