from uuid import UUID

from src.application.dto.bondholder import BondHolderDTO
from src.application.use_cases.bondholder.bondholder_base import BondHolderBaseUseCase
from src.domain.exceptions import NotFoundError, InvalidTokenError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository


class BondHolderGetUseCase(BondHolderBaseUseCase):
    def __init__(
        self, bondholder_repo: BondHolderRepository, bond_repo: BondRepository
    ) -> None:
        self.bondholder_repo = bondholder_repo
        self.bond_repo = bond_repo

    async def execute(self, bondholder_id: UUID, user_id: UUID) -> BondHolderDTO:
        bondholder = await self.bondholder_repo.get_one(bondholder_id)
        if not bondholder:
            raise NotFoundError("BondHolder not found")
        if not bondholder.user_id == user_id:
            raise InvalidTokenError("User not found")
        bond = await self.bond_repo.get_one(bond_id=bondholder.bond_id)
        if not bond:
            raise NotFoundError("Bond connected to BondHolder not found")
        return await self.to_dto(bondholder=bondholder, bond=bond)


class BondHolderGetAllUseCase(BondHolderBaseUseCase):
    def __init__(
        self, bondholder_repo: BondHolderRepository, bond_repo: BondRepository
    ) -> None:
        self.bondholder_repo = bondholder_repo
        self.bond_repo = bond_repo

    async def execute(self, user_id: UUID) -> list[BondHolderDTO]:
        bh_list = await self.bondholder_repo.get_all(user_id=user_id)
        dto_list: list[BondHolderDTO] = []
        for bh in bh_list:
            bond = await self.bond_repo.get_one(bond_id=bh.bond_id)
            if not bond:
                raise NotFoundError("Bond connected to BondHolder not found")
            dto_list.append(await self.to_dto(bondholder=bh, bond=bond))
        return dto_list
