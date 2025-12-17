from src.adapters.inbound.api.dependencies.repo_deps import (
    BondRepoDep,
    ReferenceRateRepoDep,
    BondHolderRepoDep,
)
from src.application.use_cases.calculations.calculations_calculate_income import (
    CalculateIncomeUseCase,
)
from src.domain.services.bondholder_income_calculator import BondHolderIncomeCalculator


def get_calculate_income_use_case(
    bond_repo: BondRepoDep,
    reference_rate_repo: ReferenceRateRepoDep,
    bondholder_repo: BondHolderRepoDep,
) -> CalculateIncomeUseCase:
    return CalculateIncomeUseCase(
        bh_income_calculator=BondHolderIncomeCalculator(),
        bondholder_repo=bondholder_repo,
        bond_repo=bond_repo,
        reference_rate_repo=reference_rate_repo,
    )
