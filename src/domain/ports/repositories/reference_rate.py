from abc import ABC, abstractmethod
from datetime import date

from src.domain.entities.reference_rate import ReferenceRate


class ReferenceRateRepository(ABC):
    """Abstract repository for Reference rates.

    This interface defines the contract for implementing the Repository pattern.
    Concrete implementations must provide persistence for ReferenceRate entities
    in various data stores.
    """

    @abstractmethod
    async def save(self, ref_rate: ReferenceRate) -> ReferenceRate:
        pass

    @abstractmethod
    async def get_by_date(self, target_date: date) -> ReferenceRate | None:
        pass

    @abstractmethod
    async def get_latest(self) -> ReferenceRate | None:
        pass
