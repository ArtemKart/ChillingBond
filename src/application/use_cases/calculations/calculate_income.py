from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from src.application.dto.calculations import MonthlyIncomeResponseDTO
from src.application.dto.user import UserDTO
from src.application.use_cases.calculations.base import (
    CalculationsBaseUseCase,
)
from src.domain.exceptions import NotFoundError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.reference_rate import ReferenceRateRepository
from src.domain.services.bondholder_income_calculator import BondHolderIncomeCalculator


class CalculateIncomeUseCase(CalculationsBaseUseCase):
    def __init__(
        self,
        bh_income_calculator: BondHolderIncomeCalculator,
        bondholder_repo: BondHolderRepository,
        bond_repo: BondRepository,
        reference_rate_repo: ReferenceRateRepository,
    ) -> None:
        self.bh_income_calculator = bh_income_calculator
        self.bondholder_repo = bondholder_repo
        self.bond_repo = bond_repo
        self.ref_rate_repo = reference_rate_repo

    async def execute(
        self, user: UserDTO, target_date: date
    ) -> MonthlyIncomeResponseDTO:
        bondholders = await self.bondholder_repo.get_all(user_id=user.id)
        if not bondholders:
            raise NotFoundError("Bondholders not found.")
        bonds_dict = await self.bond_repo.fetch_dict_from_bondholders(
            bondholders=bondholders
        )
        if not bonds_dict:
            raise NotFoundError("Bonds not found.")
        reference_rate = await self.ref_rate_repo.get_by_date(target_date=target_date)
        if not reference_rate:
            raise NotFoundError("Reference rate not found for the given date.")
        income_data = {}
        for bh in bondholders:
            bond = bonds_dict[bh.bond_id]
            income = self.bh_income_calculator.calculate_monthly_bh_income(
                bondholder=bh,
                bond=bond,
                reference_rate=reference_rate,
                day=target_date,
            )
            income_data[bh.id] = income.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self._to_dto(income_data)

    @staticmethod
    def _to_dto(data: dict[UUID, Decimal]) -> MonthlyIncomeResponseDTO:
        return MonthlyIncomeResponseDTO(data=data)
