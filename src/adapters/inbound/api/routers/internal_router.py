import logging
from fastapi import APIRouter, Depends

from src.adapters.inbound.api.dependencies.event_publisher_deps import EventPublisherDep
from src.adapters.inbound.api.dependencies.repo_deps import (
    BondHolderRepoDep,
    BondRepoDep,
    UserRepoDep
)
from src.application.use_cases.bondholder.bondholder_check_matured import CheckMaturedBondHolderUseCase
from src.domain.services.bondholder_maturity_checker import BondHolderMaturityChecker

logger = logging.getLogger(__name__)

internal_router = APIRouter(prefix="/internal", tags=["internal"])


@internal_router.post("/check-matured-bondholders")
async def check_matured_bondholders(
    bondholder_repository: BondHolderRepoDep,
    bond_repository: BondRepoDep,
    user_repository: UserRepoDep,
    event_publisher: EventPublisherDep
):
    """
    Internal endpoint: check for matured bondholders.
    This endpoint is called by the scheduler daily.
    """
    logger.info("Starting scheduled maturity check")

    use_case = CheckMaturedBondHolderUseCase(
        bondholder_repository=bondholder_repository,
        bond_repository=bond_repository,
        user_repository=user_repository,
        maturity_checker=BondHolderMaturityChecker(),
        event_publisher=event_publisher
    )

    matured_count = await use_case.execute()

    logger.info(
        "Maturity check completed",
        extra={"matured_count": matured_count}
    )

    return {
        "status": "success",
        "matured_count": matured_count
    }
