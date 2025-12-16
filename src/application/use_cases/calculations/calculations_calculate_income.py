from datetime import date
from decimal import Decimal
from uuid import UUID

from src.application.dto.calculations import MonthlyIncomeResponseDTO
from src.application.use_cases.calculations.calculations_base import (
    CalculationsBaseUseCase,
)
from src.domain.exceptions import NotFoundError
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.services.bondholder_income_calculator import BondHolderIncomeCalculator


class CalculateIncomeUseCase(CalculationsBaseUseCase):
    def __init__(
        self,
        bh_income_calculator: BondHolderIncomeCalculator,
        bondholder_repo: BondHolderRepository,
        bond_repo: BondRepository,
        reference_rate_repo,
    ) -> None:
        self.bh_income_calculator = bh_income_calculator
        self.bondholder_repo = bondholder_repo
        self.bond_repo = bond_repo
        self.ref_rate_repo = reference_rate_repo

    async def execute(
        self, bondholder_id: UUID, target_date: date
    ) -> MonthlyIncomeResponseDTO:
        bondholder = await self.bondholder_repo.get_one(bondholder_id=bondholder_id)
        if not bondholder:
            raise NotFoundError("Bondholder not found.")
        bond = await self.bond_repo.get_one(bond_id=bondholder.bond_id)
        if not bond:
            raise NotFoundError("Bond not found.")
        reference_rate = await self.ref_rate_repo.get_by_date(target_date=target_date)

        income = self.bh_income_calculator.calculate_monthly_bh_income(
            bondholder=bondholder,
            bond=bond,
            reference_rate=reference_rate,
            day=target_date,
        )
        return self._to_dto(income)

    @staticmethod
    def _to_dto(income: Decimal) -> MonthlyIncomeResponseDTO:
        return MonthlyIncomeResponseDTO(value=income)
