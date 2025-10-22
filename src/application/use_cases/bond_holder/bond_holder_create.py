from uuid import uuid4

from src.application.dto.bond import BondCreateDTO
from src.application.dto.bond_holder import BondHolderCreateDTO, BondHolderDTO
from src.application.use_cases.bond_holder.bond_holder_base import BondHolderBaseUseCase
from src.domain.entities.bond_holder import BondHolder as BondHolderEntity
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bond_holder import BondHolderRepository
from src.domain.entities.bond import Bond as BondEntity


class BondHolderCreateUseCase(BondHolderBaseUseCase):
    def __init__(
        self, bond_repo: BondRepository, bond_holder_repo: BondHolderRepository
    ) -> None:
        self.bond_repo = bond_repo
        self.bond_holder_repo = bond_holder_repo

    async def execute(
        self, bh_dto: BondHolderCreateDTO, b_dto: BondCreateDTO
    ) -> BondHolderDTO:
        bond = await self.bond_repo.get_by_series(b_dto.series)
        if bond:
            new_bh = BondHolderEntity(
                id=uuid4(),
                bond_id=bond.id,
                user_id=bh_dto.user_id,
                quantity=bh_dto.quantity,
                purchase_date=bh_dto.purchase_date,
            )
            await self.bond_holder_repo.write(new_bh)
            return await self.to_dto(bond_holder=new_bh, bond=bond)

        new_bond = BondEntity(
            id=uuid4(),
            series=b_dto.series,
            nominal_value=b_dto.nominal_value,
            maturity_period=b_dto.maturity_period,
            initial_interest_rate=b_dto.initial_interest_rate,
            first_interest_period=b_dto.first_interest_period,
            reference_rate_margin=b_dto.reference_rate_margin,
        )
        new_bond = await self.bond_repo.write(new_bond)

        new_bh = BondHolderEntity(
            id=uuid4(),
            bond_id=new_bond.id,
            user_id=bh_dto.user_id,
            quantity=bh_dto.quantity,
            purchase_date=bh_dto.purchase_date,
        )
        new_bh = await self.bond_holder_repo.write(new_bh)
        return await self.to_dto(bond_holder=new_bh, bond=new_bond)
