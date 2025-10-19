from typing import Annotated

from fastapi import Depends

from src.adapters.inbound.api.dependencies import SessionDep
from src.adapters.outbound.repositories.bond import SQLAlchemyBondRepository
from src.adapters.outbound.repositories.user import SQLAlchemyUserRepository


def get_user_repository(session: SessionDep) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


def get_bond_repository(session: SessionDep) -> SQLAlchemyBondRepository:
    return SQLAlchemyBondRepository(session)


UserRepoDep = Annotated[SQLAlchemyUserRepository, Depends(get_user_repository)]
BondRepoDep = Annotated[SQLAlchemyBondRepository, Depends(get_bond_repository)]
