import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from src.adapters.inbound.api.dependencies.use_cases.ref_rate_deps import (
    update_ref_rate_use_case,
)
from src.application.use_cases.reference_rate.update import UpdateReferenceRateUseCase

logger = logging.getLogger(__name__)

internal_router = APIRouter(prefix="/internal", tags=["internal"])


@internal_router.get("/update-reference-rates")
async def update_reference_rates(
    use_case: Annotated[UpdateReferenceRateUseCase, Depends(update_ref_rate_use_case)],
):
    """
    Internal endpoint: update NBP reference rates.
    This endpoint is called by the scheduler every 3 days.
    """
    logger.info("Starting scheduled NBP rate update")

    result = await use_case.execute()

    logger.info(
        "NBP rate update completed",
        extra={"success": result.success, "rate_changed": result.rate_changed},
    )

    return {
        "status": "success" if result.success else "error",
        "rate_changed": result.rate_changed,
        "message": result.message,
    }
