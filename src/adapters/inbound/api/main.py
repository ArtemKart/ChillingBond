from typing import Final

from fastapi import FastAPI

from src.adapters.exceptions import SQLAlchemyRepositoryError
from src.adapters.inbound.api.exception_handlers import (
    domain_exception_handler,
    repository_exception_handler,
)
from src.adapters.inbound.api.routers.bond_router import bond_router
from src.adapters.inbound.api.routers.login_router import login_router
from src.adapters.inbound.api.routers.user_router import user_router
from src.domain.exceptions import DomainError

app: Final = FastAPI()


app.include_router(user_router)
app.include_router(bond_router)
app.include_router(login_router)


app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(SQLAlchemyRepositoryError, repository_exception_handler)
