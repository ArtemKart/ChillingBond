from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.bond_holder import BondHolder


class BondHolderRepository(ABC):
    """Abstract repository for managing holding bonds.

    This interface defines the contract for implementing the Repository pattern.
    Concrete implementations must provide persistence for BondHolder entities
    in various data stores.
    """

    @abstractmethod
    async def get_one(self, bond_holder_id: UUID) -> BondHolder | None:
        pass

    @abstractmethod
    async def get_all(self, user_id: UUID) -> list[BondHolder]:
        pass

    @abstractmethod
    async def write(self, entity: BondHolder) -> BondHolder:
        pass

    @abstractmethod
    async def update(self, entity: BondHolder) -> BondHolder:
        pass
