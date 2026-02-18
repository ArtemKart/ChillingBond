from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.bond import Bond
from src.domain.entities.bondholder import BondHolder


class BondRepository(ABC):
    """Abstract repository for managing bond entities.

    This interface defines the contract for implementing the Repository pattern.
    Concrete implementations must provide persistence for Bond entities
    in various data stores.
    """

    @abstractmethod
    async def get_one(self, bond_id: UUID) -> Bond | None:
        """Retrieves a bond by its identifier.

        Args:
            bond_id: The unique identifier of the bond.

        Returns:
            A Bond object if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_many(self, ids: list[UUID]) -> list[Bond]:
        """Retrieves a list of bonds matching the given identifiers.

        Args:
            ids: The identifiers of the bonds to retrieve.

        Returns:
            A list of Bond objects matching the given identifiers.
        """

    @abstractmethod
    async def get_by_series(self, series: str) -> Bond | None:
        """Retrieves a bond by series.
        Args:
            series: The unique series identifier.

        Returns:
            A Bond object if found, None otherwise
        """
        pass

    @abstractmethod
    async def write(self, bond: Bond) -> Bond:
        """Creates a new bond in the repository.

        Args:
            bond: The Bond object to persist.

        Returns:
            The persisted Bond object if created, None otherwise.
        """
        pass

    @abstractmethod
    async def update(self, bond: Bond) -> Bond:
        """Updates an existing bond in the repository.

        Args:
            bond: The Bond object with updated data.

        Returns:
            The updated Bond object if updated, None otherwise.
        """
        pass

    @abstractmethod
    async def delete(self, bond_id: UUID) -> Bond | None:
        """Deletes a bond from the repository.

        Args:
            bond_id: The unique identifier of the bondholder to delete.

        Returns:
            The deleted Bond object if deleted, None otherwise.
        """
        pass

    @abstractmethod
    async def fetch_dict_from_bondholders(self, bondholders: list[BondHolder]) -> dict[UUID, Bond]:
        """Fetch bonds from the repository by passed bondholders.

        Args:
            bondholders: list of Bondholder objects.

        Returns:
            A dictionary mapping bond UUIDs to Bond objects.
        """
        pass
