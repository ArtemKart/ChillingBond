from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import ConflictError
from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.domain.entities.user import User as UserEntity
from src.domain.ports.repositories.user import UserRepository
from src.adapters.outbound.database.models import User as UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user(self, user_id: UUID) -> UserEntity | None:
        model = await self._session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        return self._to_entity(user) if user else None

    async def write(self, user: UserEntity) -> UserEntity:
        if await self.get_user_by_email(user.email):
            raise ConflictError("User with given email address already exists")
        try:
            model = self._to_model(user)
            self._session.add(model)
            await self._session.commit()
            await self._session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            error_msg = "User already exists or constraint violated"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e
        except SQLAlchemyError as e:
            error_msg = "Failed to save user"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    async def delete(self, user_id: UUID) -> None:
        try:
            model = await self._session.get(UserModel, user_id)
            if not model:
                raise ConflictError("User not found")
            await self._session.delete(model)
            await self._session.commit()
        except SQLAlchemyError as e:
            error_msg = "Failed to delete user"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    @staticmethod
    def _to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=model.email,
            hashed_password=model.password,
            name=model.name,
        )

    @staticmethod
    def _to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            password=entity.hashed_password,
            name=entity.name,
        )

    @staticmethod
    def _update_model(model: UserModel, entity: UserEntity) -> None:
        model.email = entity.email
        model.password = entity.hashed_password
        model.name = entity.name
