from src.application.dto.bondholder import BondHolderDTO, BondHolderChangeQuantityDTO
from src.application.use_cases.bondholder.bondholder_base import BondHolderBaseUseCase
from src.domain.exceptions import NotFoundError, InvalidTokenError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.user import UserRepository


class BondAddToBondHolderUseCase(BondHolderBaseUseCase):
    """Adds new bonds to existing BondHolder"""

    def __init__(
        self,
        bond_repo: BondRepository,
        user_repo: UserRepository,
        bondholder_repo: BondHolderRepository,
    ) -> None:
        self.bond_repo = bond_repo
        self.user_repo = user_repo
        self.bondholder_repo = bondholder_repo

    async def execute(self, dto: BondHolderChangeQuantityDTO) -> BondHolderDTO:
        bondholder = await self.bondholder_repo.get_one(bondholder_id=dto.id)
        if not bondholder:
            raise NotFoundError("Bond holder not found")
        if bondholder.user_id != dto.user_id:
            raise InvalidTokenError("Not authenticated")
        if dto.is_positive:
            bondholder.add_quantity(dto.quantity)
        else:
            bondholder.reduce_quantity(dto.quantity)
        bondholder = await self.bondholder_repo.update(bondholder)
        bond = await self.bond_repo.get_one(bondholder.bond_id)
        if not bond:
            raise NotFoundError("Bond connected to BondHolder not found")
        return self.to_dto(bond=bond, bondholder=bondholder)
