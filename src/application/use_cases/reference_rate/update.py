from dataclasses import dataclass
from datetime import date
from decimal import Decimal


from src.application.events.event_publisher import EventPublisher
from src.domain.ports.repositories.reference_rate import ReferenceRateRepository
from src.domain.ports.services.reference_rate_provider import ReferenceRateProvider
from src.domain.entities.reference_rate import ReferenceRate as ReferenceRateEntity


class UpdateReferenceRateUseCase:
    """
    Use case for periodically updating reference rates.

    Workflow:
    1. Fetch current rate from external provider
    2. Get latest rate from database
    3. Compare them
    4. If different - publish ReferenceRateHasChanged event
    5. Event handler will save the new rate to DB
    """

    def __init__(
        self,
        reference_rate_repo: ReferenceRateRepository,
        rate_provider: ReferenceRateProvider,
        event_publisher: EventPublisher,
    ) -> None:
        self._ref_rate_repo = reference_rate_repo
        self._rate_provider = rate_provider
        self._event_publisher = event_publisher

    async def execute(self) -> "UpdateReferenceRatesResult":
        try:
            current_rate_value, current_effective_date = (
                await self._rate_provider.get_current_rate()
            )

            latest_rate = await self._ref_rate_repo.get_latest()
            if latest_rate and self._rates_are_same(
                latest_rate.value,
                latest_rate.start_date,
                current_rate_value,
                current_effective_date,
            ):
                return UpdateReferenceRatesResult(
                    success=True,
                    rate_changed=False,
                    message="Rate has not changed",
                    rate_value=latest_rate.value,
                    effective_date=latest_rate.start_date,
                )
            reference_rate = ReferenceRateEntity.create(
                value=current_rate_value,
                start_date=current_effective_date,
            )
            await self._ref_rate_repo.save(ref_rate=reference_rate)
            return UpdateReferenceRatesResult(
                success=True,
                rate_changed=True,
                message="New rate detected and event published",
                rate_value=current_rate_value,
                effective_date=current_effective_date,
            )

        except Exception as e:
            return UpdateReferenceRatesResult(
                success=False, rate_changed=False, message=f"Failed to update: {str(e)}"
            )

    @staticmethod
    def _rates_are_same(
        db_rate_value: Decimal,
        db_effective_date: date,
        current_rate_value: Decimal,
        current_effective_date: date,
    ) -> bool:
        """
        Compare two rates to check if they are the same.

        Args:
            db_rate_value: Rate value from database
            db_effective_date: Effective date from database
            current_rate_value: Current rate value
            current_effective_date: Current effective date

        Returns:
            True if rates are the same
        """
        return (
            db_rate_value == current_rate_value
            and db_effective_date == current_effective_date
        )


@dataclass
class UpdateReferenceRatesResult:
    """Result of the update reference rates use case."""

    success: bool
    rate_changed: bool
    message: str
    rate_value: Decimal | None = None
    effective_date: date | None = None
