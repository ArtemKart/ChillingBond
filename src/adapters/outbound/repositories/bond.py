from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.exceptions import SQLAlchemyRepositoryError
from src.domain.entities.bond import Bond as BondEntity
from src.adapters.outbound.database.models import Bond as BondModel
from src.domain.ports.repositories.bond import BondRepository


class SQLAlchemyBondRepository(BondRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_one(self, bond_id: UUID) -> BondEntity | None:
        model = await self._session.get(BondModel, bond_id)
        if model:
            return self._to_entity(model)
        return None

    async def get_by_series(self, series: str) -> BondEntity | None:
        res = await self._session.execute(
            select(BondModel).where(BondModel.series == series)
        )
        model = res.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def write(self, bond: BondEntity) -> BondEntity:
        try:
            model = self._to_model(bond)
            self._session.add(model)
            await self._session.commit()
            await self._session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            error_msg = "Bond already exists or constraint violated"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e
        except SQLAlchemyError as e:
            error_msg = "Failed to save bond"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    async def update(self, bond: BondEntity) -> BondEntity:
        try:
            model = await self._session.get(BondModel, bond.id)
            self._update_model(model, bond)
            await self._session.commit()
            await self._session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            error_msg = "Failed to update bond"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    async def delete(self, bond_id: UUID) -> None:
        try:
            model = await self._session.get(BondModel, bond_id)
            if model:
                await self._session.delete(model)
                await self._session.commit()
        except SQLAlchemyError as e:
            error_msg = "Failed to delete bond"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    @staticmethod
    def _to_entity(model: BondModel) -> BondEntity:
        return BondEntity(
            id=model.id,
            nominal_value=model.nominal_value,
            series=model.series,
            maturity_period=model.maturity_period,
            initial_interest_rate=model.initial_interest_rate,
            first_interest_period=model.first_interest_period,
            reference_rate_margin=model.reference_rate_margin,
        )

    @staticmethod
    def _to_model(entity: BondEntity) -> BondModel:
        return BondModel(
            id=entity.id,
            nominal_value=entity.nominal_value,
            series=entity.series,
            maturity_period=entity.maturity_period,
            initial_interest_rate=entity.initial_interest_rate,
            first_interest_period=entity.first_interest_period,
            reference_rate_margin=entity.reference_rate_margin,
        )

    @staticmethod
    def _update_model(model: BondModel, entity: BondEntity) -> None:
        model.nominal_value = entity.nominal_value
        model.series = entity.series
        model.maturity_period = entity.maturity_period
        model.initial_interest_rate = entity.initial_interest_rate
        model.first_interest_period = entity.first_interest_period
        model.reference_rate_margin = entity.reference_rate_margin
