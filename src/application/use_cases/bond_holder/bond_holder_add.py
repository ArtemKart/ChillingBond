from src.application.dto.bond_holder import BondHolderDTO, BondHolderChangeQuantityDTO
from src.application.use_cases.bond_holder.bond_holder_base import BondHolderBaseUseCase
from src.domain.exceptions import NotFoundError, AuthorizationError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bond_holder import BondHolderRepository
from src.domain.ports.repositories.user import UserRepository


class BondAddToBondHolderUseCase(BondHolderBaseUseCase):
    """Adds new bonds to existing BondHolder"""

    def __init__(
        self,
        bond_repo: BondRepository,
        user_repo: UserRepository,
        bond_holder_repo: BondHolderRepository,
    ) -> None:
        self.bond_repo = bond_repo
        self.user_repo = user_repo
        self.bond_holder_repo = bond_holder_repo

    async def execute(self, dto: BondHolderChangeQuantityDTO) -> BondHolderDTO:
        bond_holder = await self.bond_holder_repo.get_one(bond_holder_id=dto.id)
        if not bond_holder:
            raise NotFoundError("Bond holder not found")
        if bond_holder.user_id != dto.user_id:
            raise AuthorizationError("Access denied")
        if dto.is_positive:
            bond_holder.add_quantity(dto.quantity)
        else:
            bond_holder.reduce_quantity(dto.quantity)
        bond_holder = await self.bond_holder_repo.update(bond_holder)
        bond = await self.bond_repo.get_one(bond_holder.bond_id)
        if not bond:
            raise NotFoundError("Bond connected to BondHolder not found")
        return self.to_dto(bond=bond, bond_holder=bond_holder)
