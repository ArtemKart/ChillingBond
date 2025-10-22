from src.adapters.inbound.api.dependencies.repo_deps import (
    BondRepoDep,
    UserRepoDep,
    BondHolderRepoDep,
)
from src.application.use_cases.bond_holder.bond_holder_add import (
    BondAddToBondHolderUseCase,
)
from src.application.use_cases.bond_holder.bond_holder_create import (
    BondHolderCreateUseCase,
)
from src.application.use_cases.bond_holder.bond_holder_get import (
    BondHolderGetUseCase,
    BondHolderGetAllUseCase,
)
from src.application.use_cases.bond_holder.bond_update import BondUpdateUseCase


def bond_add_to_bh_use_case(
    bond_repo: BondRepoDep,
    user_repo: UserRepoDep,
    bond_holder_repo: BondHolderRepoDep,
) -> BondAddToBondHolderUseCase:
    return BondAddToBondHolderUseCase(
        bond_repo=bond_repo, user_repo=user_repo, bond_holder_repo=bond_holder_repo
    )


def bond_update_use_case(
    bond_repo: BondRepoDep,
) -> BondUpdateUseCase:
    return BondUpdateUseCase(bond_repo=bond_repo)


def create_bond_holder_use_case(
    bond_repo: BondRepoDep,
    bond_holder_repo: BondHolderRepoDep,
) -> BondHolderCreateUseCase:
    return BondHolderCreateUseCase(
        bond_repo=bond_repo,
        bond_holder_repo=bond_holder_repo,
    )


def bh_get_use_case(
    bond_repo: BondRepoDep, bond_holder_repo: BondHolderRepoDep
) -> BondHolderGetUseCase:
    return BondHolderGetUseCase(
        bond_repo=bond_repo,
        bond_holder_repo=bond_holder_repo,
    )


def bh_get_all_use_case(
    bond_repo: BondRepoDep, bond_holder_repo: BondHolderRepoDep
) -> BondHolderGetAllUseCase:
    return BondHolderGetAllUseCase(
        bond_repo=bond_repo,
        bond_holder_repo=bond_holder_repo,
    )
