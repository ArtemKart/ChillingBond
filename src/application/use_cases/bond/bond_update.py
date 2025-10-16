from uuid import UUID

from src.application.dto.bond import BondDTO, BondUpdateDTO
from src.application.use_cases.bond.bond_base import BondBaseUseCase
from src.domain.exceptions import NotFoundError
from src.domain.repositories.bond import BondRepository


class BondUpdateUseCase(BondBaseUseCase):
    def __init__(self, bond_repo: BondRepository) -> None:
        self.bond_repo = bond_repo

    async def execute(self, dto: BondUpdateDTO, bond_id: UUID, user_id: UUID) -> BondDTO:  # type: ignore[return]
        bond = self.bond_repo.get_one(bond_id)
        if not bond:
            raise NotFoundError("Bond not found")
        pass
