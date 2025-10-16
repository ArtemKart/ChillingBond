from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.adapters.inbound.api.dependencies import get_bond_create_use_case, BondRepoDep
from src.adapters.inbound.api.schemas.bond import BondResponse, BondCreate, BondUpdate
from src.application.dto.bond import BondCreateDTO, BondUpdateDTO
from src.application.use_cases.bond.bond_create import BondCreateUseCase
from src.application.use_cases.bond.bond_update import BondUpdateUseCase

bond_router = APIRouter(prefix="/bonds", tags=["bond"])

@bond_router.post("", response_model=BondResponse)
async def create_bond(
    bond_data: BondCreate,
    use_case: Annotated[BondCreateUseCase, Depends(get_bond_create_use_case)],
):
    dto = BondCreateDTO(
        buy_date=bond_data.buy_date,
        nominal_value=bond_data.nominal_value,
        series=bond_data.series,
        maturity_period=bond_data.maturity_period,
        initial_interest_rate=bond_data.initial_interest_rate,
        first_interest_period=bond_data.first_interest_period,
        reference_rate_margin=bond_data.reference_rate_margin,
        user_id=bond_data.user_id,
    )
    return await use_case.execute(dto=dto)


@bond_router.get("/{bond_id}", response_model=BondResponse)
async def get_bond(bond_id: UUID, repo: BondRepoDep):
    bond = await repo.get_one(bond_id)
    if not bond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bond not found")
    return bond


@bond_router.get("/all/{user_id}", response_model=list[BondResponse])
async def get_bonds(user_id: UUID, repo: BondRepoDep):
    return await repo.get_all(user_id=user_id)


@bond_router.put("/{bond_id}/user/{user_id}", response_model=BondResponse)
async def update_bond(
    bond_id: UUID,
    user_id: UUID, # TODO: replace with check permissions using get_current_user
    bond_data: BondUpdate,
    use_case: Annotated[BondUpdateUseCase, Depends(get_bond_create_use_case)],
):
    dto = BondUpdateDTO(
        buy_date=bond_data.buy_date,
        nominal_value=bond_data.nominal_value,
        series=bond_data.series,
        maturity_period=bond_data.maturity_period,
        initial_interest_rate=bond_data.initial_interest_rate,
        first_interest_period=bond_data.first_interest_period,
        reference_rate_margin=bond_data.reference_rate_margin,
    )
    await use_case.execute(dto=dto, bond_id=bond_id, user_id=user_id)
