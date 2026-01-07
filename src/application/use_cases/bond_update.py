from dataclasses import asdict
from uuid import UUID

from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.application.dto.bond import BondDTO, BondUpdateDTO
from src.domain.exceptions import NotFoundError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.entities.bond import Bond as BondEntity


class BondUpdateUseCase:
    def __init__(
        self, bond_repo: BondRepository, bh_repo: BondHolderRepository
    ) -> None:
        self.bh_repo: BondHolderRepository = bh_repo
        self.bond_repo: BondRepository = bond_repo

    async def execute(self, dto: BondUpdateDTO, bh_id: UUID) -> BondDTO:
        bh = await self.bh_repo.get_one(bondholder_id=bh_id)
        if not bh:
            raise NotFoundError("BondHolder not found")
        bond = await self.bond_repo.get_one(bond_id=bh.bond_id)
        update_attr = {k: v for k, v in asdict(dto).items() if v}
        for attr, value in update_attr.items():
            setattr(bond, attr, value)
        new_bond = await self.bond_repo.update(bond)
        return self._to_dto(new_bond)

    @staticmethod
    def _to_dto(bond: BondEntity) -> BondDTO:
        return BondDTO(
            id=bond.id,
            nominal_value=bond.nominal_value,
            series=bond.series,
            maturity_period=bond.maturity_period,
            initial_interest_rate=bond.initial_interest_rate,
            first_interest_period=bond.first_interest_period,
            reference_rate_margin=bond.reference_rate_margin,
        )
