from src.application.dto.bondholder import BondHolderDTO, BondHolderChangeQuantityDTO
from src.application.use_cases.bondholder.base import BondHolderBaseUseCase
from src.domain.exceptions import NotFoundError, InvalidTokenError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.user import UserRepository


class ChangeBondHolderQuantityUseCase(BondHolderBaseUseCase):
    """Change bond quantity in existing bondholder"""

    def __init__(
        self,
        bond_repo: BondRepository,
        user_repo: UserRepository,
        bondholder_repo: BondHolderRepository,
    ) -> None:
        self.bond_repo: BondRepository = bond_repo
        self.user_repo: UserRepository = user_repo
        self.bondholder_repo: BondHolderRepository = bondholder_repo

    async def execute(self, dto: BondHolderChangeQuantityDTO) -> BondHolderDTO:
        bondholder = await self.bondholder_repo.get_one(bondholder_id=dto.id)
        if not bondholder:
            raise NotFoundError("Bond holder not found")
        if bondholder.user_id != dto.user_id:
            raise InvalidTokenError("Not authenticated")
        bondholder.change_quantity(dto.new_quantity)
        bondholder = await self.bondholder_repo.update(bondholder)
        bond = await self.bond_repo.get_one(bondholder.bond_id)
        if not bond:
            raise NotFoundError("Bond connected to BondHolder not found")
        return self.to_dto(bond=bond, bondholder=bondholder)
