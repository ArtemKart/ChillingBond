from uuid import UUID

from setup_logging import setup_logging
from src.application.dto.bondholder import BondHolderDTO
from src.application.use_cases.bondholder.base import BondHolderBaseUseCase
from src.domain.exceptions import NotFoundError, AuthorizationError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository




class BondHolderGetUseCase(BondHolderBaseUseCase):
    def __init__(
        self, bondholder_repo: BondHolderRepository, bond_repo: BondRepository
    ) -> None:
        self.bondholder_repo: BondHolderRepository = bondholder_repo
        self.bond_repo: BondRepository = bond_repo

    async def execute(self, bondholder_id: UUID, user_id: UUID) -> BondHolderDTO:
        bondholder = await self.bondholder_repo.get_one(bondholder_id)
        if not bondholder:
            raise NotFoundError("BondHolder not found")
        if not bondholder.user_id == user_id:
            raise AuthorizationError("Permission denied")
        bond = await self.bond_repo.get_one(bond_id=bondholder.bond_id)
        if not bond:
            raise NotFoundError("Bond connected to BondHolder not found")
        return self.to_dto(bondholder=bondholder, bond=bond)


class BondHolderGetAllUseCase(BondHolderBaseUseCase):
    def __init__(
        self, bondholder_repo: BondHolderRepository, bond_repo: BondRepository
    ) -> None:
        self.bondholder_repo: BondHolderRepository = bondholder_repo
        self.bond_repo: BondRepository = bond_repo

    async def execute(self, user_id: UUID) -> list[BondHolderDTO]:
        import time
        import logging
        start_total = time.time()
        logger = logging.getLogger(__name__)
        logger.info(f"📊 Dashboard request started for user {user_id}")

        start_bonds = time.time()

        bh_list = await self.bondholder_repo.get_all(user_id=user_id)

        bonds_time = time.time() - start_bonds
        logger.info(f"⏱️  Bondholders fetched in {bonds_time:.4f}s (count: {len(bh_list)})")

        start_stats = time.time()
        dto_list: list[BondHolderDTO] = []
        for bh in bh_list:
            bond = await self.bond_repo.get_one(bond_id=bh.bond_id)
            if not bond:
                raise NotFoundError("Bond connected to BondHolder not found")
            dto_list.append(self.to_dto(bondholder=bh, bond=bond))
        stats_time = time.time() - start_stats
        logger.info(f"⏱️  Bond fetched in {stats_time:.4f}s")


        start_sort = time.time()
        a = sorted(dto_list, key=lambda h: h.purchase_date, reverse=True)

        sort_time = time.time() - start_sort
        logger.info(f"⏱️  Sort time in {sort_time:.4f}s")
        return a
