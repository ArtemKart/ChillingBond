import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import time
from typing import Final

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from src.adapters.config import get_config
from src.adapters.di_container import setup_event_publisher
from src.adapters.inbound.api.exception_handlers import (
    domain_exception_handler,
    repository_exception_handler,
    request_validation_exception_handler,
)
from src.adapters.inbound.api.routers.bond_router import bond_router
from src.adapters.inbound.api.routers.calculation_router import calculation_router
from src.adapters.inbound.api.routers.login_router import login_router
from src.adapters.inbound.api.routers.user_router import user_router
from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.domain.exceptions import DomainError
from src.setup_logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    config = get_config()
    logger.info(f"🔍 DATABASE_URL: {config.database_app_url}")

    event_publisher = setup_event_publisher()
    app.state.event_publisher = event_publisher

    logging.info("✅ Event Publisher initialized")

    yield


app: Final = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(user_router, prefix="/api")
app.include_router(bond_router, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(calculation_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


app.add_exception_handler(DomainError, domain_exception_handler)  # type: ignore
app.add_exception_handler(SQLAlchemyRepositoryError, repository_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore
