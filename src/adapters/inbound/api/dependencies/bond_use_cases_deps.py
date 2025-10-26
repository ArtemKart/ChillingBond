from src.adapters.inbound.api.dependencies.repo_deps import (
    BondRepoDep,
    UserRepoDep,
    BondHolderRepoDep,
)
from src.application.use_cases.bondholder.bondholder_add import (
    BondAddToBondHolderUseCase,
)
from src.application.use_cases.bondholder.bondholder_create import (
    BondHolderCreateUseCase,
)
from src.application.use_cases.bondholder.bondholder_get import (
    BondHolderGetUseCase,
    BondHolderGetAllUseCase,
)
from src.application.use_cases.bondholder.bond_update import BondUpdateUseCase


def bond_add_to_bh_use_case(
    bond_repo: BondRepoDep,
    user_repo: UserRepoDep,
    bondholder_repo: BondHolderRepoDep,
) -> BondAddToBondHolderUseCase:
    return BondAddToBondHolderUseCase(
        bond_repo=bond_repo, user_repo=user_repo, bondholder_repo=bondholder_repo
    )


def bond_update_use_case(
    bond_repo: BondRepoDep,
) -> BondUpdateUseCase:
    return BondUpdateUseCase(bond_repo=bond_repo)


def create_bondholder_use_case(
    bond_repo: BondRepoDep,
    bondholder_repo: BondHolderRepoDep,
) -> BondHolderCreateUseCase:
    return BondHolderCreateUseCase(
        bond_repo=bond_repo,
        bondholder_repo=bondholder_repo,
    )


def bh_get_use_case(
    bond_repo: BondRepoDep, bondholder_repo: BondHolderRepoDep
) -> BondHolderGetUseCase:
    return BondHolderGetUseCase(
        bond_repo=bond_repo,
        bondholder_repo=bondholder_repo,
    )


def bh_get_all_use_case(
    bond_repo: BondRepoDep, bondholder_repo: BondHolderRepoDep
) -> BondHolderGetAllUseCase:
    return BondHolderGetAllUseCase(
        bond_repo=bond_repo,
        bondholder_repo=bondholder_repo,
    )
