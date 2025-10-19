from src.adapters.inbound.api.dependencies.repo_deps import BondRepoDep, UserRepoDep
from src.application.use_cases.bond.bond_create import BondCreateUseCase
from src.application.use_cases.bond.bond_update import BondUpdateUseCase


def get_bond_create_use_case(
    bond_repo: BondRepoDep,
    user_repo: UserRepoDep,
) -> BondCreateUseCase:
    return BondCreateUseCase(bond_repo=bond_repo, user_repo=user_repo)


def get_bond_update_use_case(
    bond_repo: BondRepoDep,
) -> BondUpdateUseCase:
    return BondUpdateUseCase(bond_repo=bond_repo)
