import logging
from contextlib import asynccontextmanager
from typing import Final
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.adapters.di_container import setup_event_publisher
from src.adapters.inbound.api.routers.calculation_router import calculation_router
from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.adapters.inbound.api.exception_handlers import (
    domain_exception_handler,
    repository_exception_handler,
    request_validation_exception_handler,
)
from src.adapters.inbound.api.routers.bond_router import bond_router
from src.adapters.inbound.api.routers.login_router import login_router
from src.adapters.inbound.api.routers.user_router import user_router
from src.domain.exceptions import DomainError
from src.setup_logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    event_publisher = setup_event_publisher()
    app.state.event_publisher = event_publisher

    logging.info("✅ Event Publisher initialized")

    yield


app: Final = FastAPI(lifespan=lifespan)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    inprogress_name="inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(bond_router)
app.include_router(login_router)
app.include_router(calculation_router)

app.add_exception_handler(DomainError, domain_exception_handler)  # type: ignore
app.add_exception_handler(SQLAlchemyRepositoryError, repository_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore
