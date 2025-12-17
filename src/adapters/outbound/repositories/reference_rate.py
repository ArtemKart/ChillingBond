from datetime import date

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.reference_rate import ReferenceRate as ReferenceRateEntity
from src.domain.ports.repositories.reference_rate import ReferenceRateRepository
from src.adapters.outbound.database.models import ReferenceRate as ReferenceRateModel


class SQLAlchemyReferenceRateRepository(ReferenceRateRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
        return result.scalar_one_or_none()

    async def get_actual(self) -> ReferenceRateEntity | None:
        pass

    @staticmethod
    def _to_entity(model: ReferenceRateModel) -> ReferenceRateEntity | None:
        return ReferenceRateEntity(
            id=model.id,
            value=model.value,
            start_date=model.start_date,
            end_date=model.end_date,
        )
