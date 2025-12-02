from datetime import date

from src.application.events.event_publisher import EventPublisher
from src.application.use_cases.bondholder.bondholder_base import BondHolderBaseUseCase
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.user import UserRepository
from src.domain.services.bondholder_maturity_checker import BondHolderMaturityChecker


class CheckMaturedBondHolderUseCase(BondHolderBaseUseCase):
    """Use Case: check all bondholders for maturity and process matured ones."""

    def __init__(
        self,
        bondholder_repository: BondHolderRepository,
        bond_repository: BondRepository,
        maturity_checker: BondHolderMaturityChecker,
        event_publisher: EventPublisher,
        user_repository: UserRepository,
    ) -> None:
        self._bondholder_repository = bondholder_repository
        self._bond_repository = bond_repository
        self._maturity_checker = maturity_checker
        self._event_publisher = event_publisher
        self._user_repository = user_repository

    async def execute(self, check_date: date | None = None) -> int:
        """
        Check all active bondholders for maturity.

        Args:
            check_date: Date to check against (defaults to today)

        Returns:
            Number of bondholders that matured
        """

        if check_date is None:
            check_date = date.today()

        bondholders = await self._bondholder_repository.get_all_active()

        if not bondholders:
            return 0

        unique_bond_ids = {bh.bond_id for bh in bondholders}
        unique_user_ids = {bh.user_id for bh in bondholders}
        
        bond_mapper = {}
        bonds = await self._bond_repository.get_by_ids(list(unique_bond_ids))
        bond_mapper = {bond.id: bond for bond in bonds}
        
        user_mapper = {}
        users = await self._user_repository.get_by_ids(list(unique_user_ids))
        user_mapper = {user.id: user for user in users}

        matured_count = 0
        for bondholder in bondholders:
            bond = bond_mapper[bondholder.bond_id]
            user = user_mapper[bondholder.user_id]

            if self._maturity_checker.is_matured(bondholder, bond, check_date):
                bondholder.mark_as_matured(
                    bond_series=bond.series,
                    user_email=user.email,
                )
                await self._bondholder_repository.update(bondholder)

                for event in bondholder.collect_events():
                    await self._event_publisher.publish(event)

                matured_count += 1
        return matured_count
