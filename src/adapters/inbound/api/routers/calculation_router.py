from datetime import date
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.adapters.inbound.api.dependencies.use_cases.calculations_deps import (
    get_calculate_income_use_case,
)
from src.application.use_cases.calculations.calculations_calculate_income import (
    CalculateIncomeUseCase,
)


calculation_router = APIRouter(prefix="/calculations", tags=["Calculations"])


@calculation_router.post("/month-income", dependencies=[Depends(current_user)])
async def calculate_income(
    use_case: Annotated[CalculateIncomeUseCase, Depends(get_calculate_income_use_case)],
    bondholder_id: UUID = Query(...),
    target_date: date = Query(
        default_factory=date.today,
        description="Date for income calculation.",
    ),
) -> Decimal:
    dto = await use_case.execute(bondholder_id=bondholder_id, target_date=target_date)
    return dto.value
