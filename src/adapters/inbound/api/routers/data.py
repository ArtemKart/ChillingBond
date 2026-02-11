from typing import Annotated

from fastapi import APIRouter, Depends

from src.adapters.inbound.api.dependencies.current_user_deps import CurrentUserDep
from src.adapters.inbound.api.dependencies.use_cases.data_deps import (
    get_equity_history_use_case,
)
from src.adapters.inbound.api.schemas.data import EquityResponse
from src.application.use_cases.data.get_equity_history import GetEquityHistoryUseCase

data_router = APIRouter(prefix="/data", tags=["Data"])


@data_router.get("equity", response_model=EquityResponse)
async def get_equity(
    user_dto: CurrentUserDep,
    use_case: Annotated[GetEquityHistoryUseCase, Depends(get_equity_history_use_case)],
):
    """
    Returns portfolio equity over time.

    - Time series of portfolio value
    - Ordered by date ascending
    """
    return await use_case.execute(user=user_dto)
