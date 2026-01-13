from uuid import UUID

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
        bondholders = await self.bondholder_repo.get_all(user_id=user_id)
        if not bondholders:
            return []
        bond_ids = [bh.bond_id for bh in bondholders]
        bonds = await self.bond_repo.get_many(bond_ids)
        bonds_dict = {bond.id: bond for bond in bonds}

        dto_list: list[BondHolderDTO] = []
        for bh in bondholders:
            bond = bonds_dict.get(bh.bond_id)
            if bond:
                dto_list.append(self.to_dto(bondholder=bh, bond=bond))

        return sorted(dto_list, key=lambda h: h.purchase_date, reverse=True)
