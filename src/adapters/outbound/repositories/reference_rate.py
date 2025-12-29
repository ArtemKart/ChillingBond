from datetime import date
from sqlite3 import IntegrityError

from sqlalchemy import select, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.domain.entities.reference_rate import ReferenceRate as ReferenceRateEntity
from src.domain.ports.repositories.reference_rate import ReferenceRateRepository
from src.adapters.outbound.database.models import ReferenceRate as ReferenceRateModel


class SQLAlchemyReferenceRateRepository(ReferenceRateRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ref_rate: ReferenceRateEntity) -> ReferenceRateEntity:
        """
        Save a ReferenceRate entity to the database.

        Args:
            ref_rate: ReferenceRate entity to be saved
        """
        try:
            model = self._to_model(ref_rate)
            self._session.add(model)
            await self._session.commit()
            await self._session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            error_msg = "ReferenceRate already exists or constraint violated"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e
        except SQLAlchemyError as e:
            error_msg = "Failed to save ReferenceRate"
            await self._session.rollback()
            raise SQLAlchemyRepositoryError(error_msg) from e

    async def get_by_date(self, target_date: date) -> ReferenceRateEntity | None:
        """
        Retrieve the reference rate that is valid for the specified date.

        Args:
            target_date: Date for which to find the applicable reference rate

        Returns:
            ReferenceRate object if found, None otherwise

        Note:
            A rate is considered valid if target_date falls between start_date
            and end_date (inclusive). If end_date is NULL, the rate is considered
            currently active with no expiration.
        """
        stmt = select(ReferenceRateModel).where(
            and_(
                ReferenceRateModel.start_date <= target_date,
                or_(
                    ReferenceRateModel.end_date >= target_date,
                    ReferenceRateModel.end_date.is_(None),
                ),
            )
        )

        result = await self._session.execute(stmt)
        result = result.scalar_one_or_none()
        return self._to_entity(result) if result else None

    async def get_latest(self) -> ReferenceRateEntity | None:
        """
        Retrieve the most recently added reference rate.
        Returns:
            ReferenceRate object if found, None otherwise
        """
        stmt = (
            select(ReferenceRateModel)
            .order_by(ReferenceRateModel.start_date.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
        
    
    async def update(self, ref_rate: ReferenceRateEntity) -> ReferenceRateEntity:
        model = await self._session.get(ReferenceRateModel, ref_rate.id)
        if not model:
            raise SQLAlchemyRepositoryError("ReferenceRate not found")
        self._update_model(model, ref_rate)
        await self._session.commit()
        return self._to_entity(model)
    
    @staticmethod
    def _to_entity(model: ReferenceRateModel) -> ReferenceRateEntity:
        return ReferenceRateEntity(
            id=model.id,
            value=model.value,
            start_date=model.start_date,
            end_date=model.end_date,
        )

    @staticmethod
    def _to_model(entity: ReferenceRateEntity) -> ReferenceRateModel:
        return ReferenceRateModel(
            id=entity.id,
            value=entity.value,
            start_date=entity.start_date,
            end_date=entity.end_date,
        )
        
    @staticmethod
    def _update_model(model: ReferenceRateModel, entity: ReferenceRateEntity) -> None:
        model.value = entity.value
        model.start_date = entity.start_date
        model.end_date = entity.end_date
