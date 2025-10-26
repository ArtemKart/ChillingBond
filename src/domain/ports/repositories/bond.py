from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.bond import Bond


class BondRepository(ABC):
    """Abstract repository for managing bondholder entities.

    This interface defines the contract for implementing the Repository pattern.
    Concrete implementations must provide persistence for Bond entities
    in various data stores.
    """

    @abstractmethod
    async def get_one(self, bond_id: UUID) -> Bond | None:
        """Retrieves a bondholder by its identifier.

        Args:
            bond_id: The unique identifier of the bondholder.

        Returns:
            A Bond object if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_series(self, series: str) -> Bond | None:
        """Retrieves a bondholder by series.
        Args:
            series: The unique series identifier.

        Returns:
            A Bond object if found, None otherwise
        """
        pass

    @abstractmethod
    async def write(self, bond: Bond) -> Bond:
        """Creates a new bondholder in the repository.

        Args:
            bond: The Bond object to persist.

        Returns:
            The persisted Bond object.
        """
        pass

    @abstractmethod
    async def update(self, bond: Bond) -> Bond:
        """Updates an existing bondholder in the repository.

        Args:
            bond: The Bond object with updated data.

        Returns:
            The updated Bond object.
        """
        pass

    @abstractmethod
    async def delete(self, bond_id: UUID) -> None:
        """Deletes a bondholder from the repository.

        Args:
            bond_id: The unique identifier of the bondholder to delete.
        """
        pass
