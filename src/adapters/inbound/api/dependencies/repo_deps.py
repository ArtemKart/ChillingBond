from typing import Annotated

from fastapi import Depends

from src.adapters.inbound.api.dependencies import SessionDep
from src.adapters.outbound.repositories.bond import SQLAlchemyBondRepository
from src.adapters.outbound.repositories.bond_holder import (
    SQLAlchemyBondHolderRepository,
)
from src.adapters.outbound.repositories.user import SQLAlchemyUserRepository


def user_repository(session: SessionDep) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


def bond_repository(session: SessionDep) -> SQLAlchemyBondRepository:
    return SQLAlchemyBondRepository(session)


def bond_holder_repository(session: SessionDep) -> SQLAlchemyBondHolderRepository:
    return SQLAlchemyBondHolderRepository(session)


UserRepoDep = Annotated[SQLAlchemyUserRepository, Depends(user_repository)]
BondRepoDep = Annotated[SQLAlchemyBondRepository, Depends(bond_repository)]
BondHolderRepoDep = Annotated[
    SQLAlchemyBondHolderRepository, Depends(bond_holder_repository)
]
