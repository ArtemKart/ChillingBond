from typing import Annotated

from fastapi import Depends

from src.adapters.inbound.api.dependencies.event_publisher_deps import EventPublisherDep
from src.adapters.inbound.api.dependencies.repo_deps import (
    BondRepoDep,
    UserRepoDep,
    BondHolderRepoDep,
)
from src.adapters.inbound.api.dependencies.service_deps import get_bh_deletion_service
from src.application.use_cases.bondholder.bondholder_add import (
    ChangeBondHolderQuantityUseCase,
)
from src.application.use_cases.bondholder.bondholder_create import (
    BondHolderCreateUseCase,
)
from src.application.use_cases.bondholder.bondholder_delete import (
    BondHolderDeleteUseCase,
)
from src.application.use_cases.bondholder.bondholder_get import (
    BondHolderGetUseCase,
    BondHolderGetAllUseCase,
)
from src.application.use_cases.bond_update import BondUpdateUseCase
from src.domain.services.bondholder_deletion_service import BondHolderDeletionService


def bond_add_to_bh_use_case(
    bond_repo: BondRepoDep,
    user_repo: UserRepoDep,
    bondholder_repo: BondHolderRepoDep,
) -> ChangeBondHolderQuantityUseCase:
    return ChangeBondHolderQuantityUseCase(
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


def bh_delete_use_case(
    bondholder_repo: BondHolderRepoDep,
    event_publisher: EventPublisherDep,
    user_repo: UserRepoDep,
    bh_del_service: Annotated[
        BondHolderDeletionService, Depends(get_bh_deletion_service)
    ],
) -> BondHolderDeleteUseCase:
    return BondHolderDeleteUseCase(
        bondholder_repo=bondholder_repo,
        event_publisher=event_publisher,
        user_repo=user_repo,
        bh_del_service=bh_del_service,
    )
