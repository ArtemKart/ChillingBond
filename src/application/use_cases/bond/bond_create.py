from uuid import uuid4

from src.application.dto.bond import BondCreateDTO, BondDTO
from src.application.use_cases.bond.bond_base import BondBaseUseCase
from src.domain.entities.bond import Bond as BondEntity
from src.domain.exceptions import NotFoundError
from src.domain.repositories.bond import BondRepository
from src.domain.repositories.user import UserRepository


class BondCreateUseCase(BondBaseUseCase):
    def __init__(self, bond_repo: BondRepository, user_repo: UserRepository) -> None:
        self.bond_repo = bond_repo
        self.user_repo = user_repo

    async def execute(self, dto: BondCreateDTO) -> BondDTO:
        user = await self.user_repo.get_one(dto.user_id)
        if not user:
            raise NotFoundError("User not found")
        bond_entity = BondEntity(
            id=uuid4(),
            buy_date=dto.buy_date,
            nominal_value=dto.nominal_value,
            series=dto.series,
            maturity_period=dto.maturity_period,
            initial_interest_rate=dto.initial_interest_rate,
            first_interest_period=dto.first_interest_period,
            reference_rate_margin=dto.reference_rate_margin,
            user_id=dto.user_id
        )
        bond = await self.bond_repo.write(bond_entity)
        return await self.to_dto(bond)
