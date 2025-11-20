from src.adapters.inbound.api.dependencies.repo_deps import (
    BondHolderRepoDep,
    BondRepoDep,
)
from src.domain.services.bondholder_deletion_service import BondHolderDeletionService


def get_bh_deletion_service(
    bh_repo: BondHolderRepoDep,
    bond_repo: BondRepoDep,
) -> BondHolderDeletionService:
    return BondHolderDeletionService(bondholder_repo=bh_repo, bond_repo=bond_repo)
