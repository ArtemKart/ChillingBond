from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.exceptions import SQLAlchemyRepositoryError
from src.domain.ports.repositories.bond_holder import BondHolderRepository
from src.domain.entities.bond_holder import BondHolder as BondHolderEntity
from src.adapters.outbound.database.models import BondHolder as BondHolderModel


class SQLAlchemyBondHolderRepository(BondHolderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_one(self, bond_holder_id: UUID) -> BondHolderEntity | None:
        model = await self._session.get(BondHolderModel, bond_holder_id)
        if model:
            return self._to_entity(model)
        return None

    async def get_all(self, user_id: UUID) -> list[BondHolderEntity]:
        stmt = select(BondHolderModel).where(BondHolderModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def write(self, bond_holder: BondHolderEntity) -> BondHolderEntity:
        try:
            model = self._to_model(bond_holder)
            self._session.add(model)
            await self._session.commit()
            await self._session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            error_msg = "BondHolder already exists or constraint violated"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e
        except SQLAlchemyError as e:
            error_msg = "Failed to save BondHolder object"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    async def update(self, bond_holder: BondHolderEntity) -> BondHolderEntity:
        try:
            model = await self._session.get(BondHolderModel, bond_holder.id)
            self._update_model(model, bond_holder)
            await self._session.commit()
            await self._session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            error_msg = "Failed to update BondHolder object"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    @staticmethod
    def _to_entity(model: BondHolderModel) -> BondHolderEntity:
        return BondHolderEntity(
            id=model.id,
            bond_id=model.bond_id,
            user_id=model.user_id,
            quantity=model.quantity,
            purchase_date=model.purchase_date,
            last_update=model.last_update,
        )

    @staticmethod
    def _to_model(entity: BondHolderEntity) -> BondHolderModel:
        return BondHolderModel(
            id=entity.id,
            user_id=entity.user_id,
            bond_id=entity.bond_id,
            quantity=entity.quantity,
            purchase_date=entity.purchase_date,
            last_update=entity.last_update,
        )

    @staticmethod
    def _update_model(model: BondHolderModel, entity: BondHolderEntity) -> None:
        model.user_id = entity.user_id
        model.bond_id = entity.bond_id
        model.quantity = entity.quantity
        model.purchase_date = entity.purchase_date
        model.last_update = entity.last_update
