from uuid import UUID

from src.application.dto.bond_holder import BondHolderDTO
from src.application.use_cases.bond_holder.bond_holder_base import BondHolderBaseUseCase
from src.domain.exceptions import NotFoundError, AuthorizationError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bond_holder import BondHolderRepository


class BondHolderGetUseCase(BondHolderBaseUseCase):
    def __init__(
        self, bond_holder_repo: BondHolderRepository, bond_repo: BondRepository
    ) -> None:
        self.bond_holder_repo = bond_holder_repo
        self.bond_repo = bond_repo

    async def execute(self, bond_holder_id: UUID, user_id: UUID) -> BondHolderDTO:
        bond_holder = await self.bond_holder_repo.get_one(bond_holder_id)
        if not bond_holder:
            raise NotFoundError("BondHolder not found")
        if not bond_holder.user_id == user_id:
            raise AuthorizationError("Access denied")
        bond = await self.bond_repo.get_one(bond_id=bond_holder.bond_id)
        if not bond:
            raise NotFoundError("Bond connected to BondHolder not found")
        return self.to_dto(bond_holder=bond_holder, bond=bond)


class BondHolderGetAllUseCase(BondHolderBaseUseCase):
    def __init__(
        self, bond_holder_repo: BondHolderRepository, bond_repo: BondRepository
    ) -> None:
        self.bond_holder_repo = bond_holder_repo
        self.bond_repo = bond_repo

    async def execute(self, user_id: UUID) -> list[BondHolderDTO]:
        bh_list = await self.bond_holder_repo.get_all(user_id=user_id)
        dto_list: list[BondHolderDTO] = []
        for bh in bh_list:
            bond = await self.bond_repo.get_one(bond_id=bh.bond_id)
            if not bond:
                raise NotFoundError("Bond connected to BondHolder not found")
            dto_list.append(self.to_dto(bond_holder=bh, bond=bond))
        return dto_list
