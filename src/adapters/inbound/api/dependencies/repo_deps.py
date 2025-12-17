from typing import Annotated

from fastapi import Depends

from src.adapters.inbound.api.dependencies import SessionDep
from src.adapters.outbound.repositories.bond import SQLAlchemyBondRepository
from src.adapters.outbound.repositories.bondholder import (
    SQLAlchemyBondHolderRepository,
)
from src.adapters.outbound.repositories.user import SQLAlchemyUserRepository
from src.adapters.outbound.repositories.reference_rate import SQLAlchemyReferenceRateRepository

def user_repository(session: SessionDep) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


def bond_repository(session: SessionDep) -> SQLAlchemyBondRepository:
    return SQLAlchemyBondRepository(session)


def bondholder_repository(session: SessionDep) -> SQLAlchemyBondHolderRepository:
    return SQLAlchemyBondHolderRepository(session)


def reference_rate_repository(session: SessionDep) -> SQLAlchemyReferenceRateRepository:
    return SQLAlchemyReferenceRateRepository(session)


UserRepoDep = Annotated[SQLAlchemyUserRepository, Depends(user_repository)]
BondRepoDep = Annotated[SQLAlchemyBondRepository, Depends(bond_repository)]
BondHolderRepoDep = Annotated[
    SQLAlchemyBondHolderRepository, Depends(bondholder_repository)
]
ReferenceRateRepoDep = Annotated[
    SQLAlchemyReferenceRateRepository, Depends(reference_rate_repository)
]
