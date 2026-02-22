from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.adapters.inbound.api.dependencies.current_user_deps import CurrentUserDep
from src.adapters.inbound.api.dependencies.use_cases.calculations_deps import (
    get_calculate_income_use_case,
)
from src.adapters.inbound.api.schemas.calculations import MonthIncomeResponse
from src.application.use_cases.calculations.calculate_income import (
    CalculateIncomeUseCase,
)

calculations_router = APIRouter(prefix="/calculations", tags=["Calculations"])


@calculations_router.post("/month-income", response_model=MonthIncomeResponse)
async def calculate_income(
    user_dto: CurrentUserDep,
    use_case: Annotated[CalculateIncomeUseCase, Depends(get_calculate_income_use_case)],
    target_date: Annotated[date, Query(description="Date for income calculation.")] = date.today(),
):
    return await use_case.execute(user=user_dto, target_date=target_date)
