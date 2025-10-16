from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.outbound.database.engine import get_session
from src.adapters.outbound.repositories.bond import SQLAlchemyBondRepository
from src.adapters.outbound.repositories.user import SQLAlchemyUserRepository
from src.adapters.outbound.security.bcrypt_hasher import BcryptPasswordHasher
from src.application.use_cases.bond.bond_create import BondCreateUseCase
from src.application.use_cases.bond.bond_update import BondUpdateUseCase
from src.application.use_cases.user.user_create import UserCreateUseCase

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


def get_bond_repository(session: SessionDep) -> SQLAlchemyBondRepository:
    return SQLAlchemyBondRepository(session)


def get_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


UserRepoDep = Annotated[
    SQLAlchemyUserRepository, Depends(get_user_repository)
]
BondRepoDep = Annotated[
    SQLAlchemyBondRepository, Depends(get_bond_repository)
]
HasherDep = Annotated[BcryptPasswordHasher, Depends(get_hasher)]


def get_user_create_use_case(
    user_repo: UserRepoDep,
    hasher: HasherDep,
) -> UserCreateUseCase:
    return UserCreateUseCase(user_repo=user_repo, hasher=hasher)


def get_bond_create_use_case(
    bond_repo: BondRepoDep,
    user_repo: UserRepoDep,
) -> BondCreateUseCase:
    return BondCreateUseCase(bond_repo=bond_repo, user_repo=user_repo)


def get_bond_update_use_case(
    bond_repo: BondRepoDep,
) -> BondUpdateUseCase:
    return BondUpdateUseCase(bond_repo=bond_repo)
