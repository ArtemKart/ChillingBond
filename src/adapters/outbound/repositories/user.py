from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.exceptions import SQLAlchemyRepositoryError
from src.domain.entities.user import User as UserEntity
from src.domain.repositories.user import UserRepository
from src.adapters.outbound.database.models import User as UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_one(self, user_id: UUID) -> UserEntity | None:
        model = await self._session.get(UserModel, user_id)
        if model:
            return await self._to_entity(model)
        return None

    async def write(self, user: UserEntity) -> UserEntity:
        try:
            model = await self._to_model(user)
            self._session.add(model)
            await self._session.commit()
            await self._session.refresh(model)
            return await self._to_entity(model)
        except IntegrityError as e:
            error_msg = "User already exists or constraint violated"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e
        except SQLAlchemyError as e:
            error_msg = "Failed to save user"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    async def update(self, user: UserEntity) -> UserEntity:
        try:
            model = self._session.get(UserModel, user.id)
            await self._update_model(model, user)
            await self._session.commit()
            await self._session.refresh(model)
            return await self._to_entity(model)
        except SQLAlchemyError as e:
            error_msg = "Failed to update user"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    async def delete(self, user_id: UUID) -> None:
        try:
            model = self._session.get(UserModel, user_id)
            if model:
                await self._session.delete(model)
                await self._session.commit()
        except SQLAlchemyError as e:
            error_msg = "Failed to delete user"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    @staticmethod
    async def _to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=model.email,
            password=model.password,
            name=model.name,
        )

    @staticmethod
    async def _to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            password=entity.password,
            name=entity.name,
        )

    @staticmethod
    async def _update_model(model: UserModel, entity: UserEntity) -> None:
        model.email = entity.email
        model.password = entity.password
        model.name = entity.name
