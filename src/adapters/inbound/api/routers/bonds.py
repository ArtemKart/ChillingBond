from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.adapters.inbound.api.dependencies.use_cases.bond_deps import (
    bh_delete_use_case,
    bh_get_all_use_case,
    bh_get_use_case,
    update_bh_quantity_use_case,
    bh_create_use_case,
)
from src.adapters.inbound.api.dependencies.current_user_deps import (
    CurrentUserDep,
)
from src.adapters.inbound.api.schemas.bondholder import (
    BondHolderChangeRequest,
    BondHolderCreateRequest,
    BondHolderResponse,
)
from src.application.dto.bond import BondCreateDTO
from src.application.dto.bondholder import (
    BondHolderUpdateQuantityDTO,
    BondHolderCreateDTO,
)
from src.application.use_cases.bondholder.bh_update_quantity import (
    UpdateBondHolderQuantityUseCase,
)
from src.application.use_cases.bondholder.bh_create import (
    BondHolderCreateUseCase,
)
from src.application.use_cases.bondholder.bh_delete import (
    BondHolderDeleteUseCase,
)
from src.application.use_cases.bondholder.bh_get import (
    BondHolderGetAllUseCase,
    BondHolderGetUseCase,
)
from src.domain.exceptions import NotFoundError

bond_router = APIRouter(prefix="/bonds", tags=["bondholder"])


@bond_router.post(
    "",
    response_model=BondHolderResponse,
    status_code=status.HTTP_201_CREATED,
    description="Buy bonds. Create bond holder",
)
async def create_bond_purchase(
    bondholder_data: BondHolderCreateRequest,
    user: CurrentUserDep,
    use_case: Annotated[BondHolderCreateUseCase, Depends(bh_create_use_case)],
):
    bondholder_dto = BondHolderCreateDTO(
        user_id=user.id,
        quantity=bondholder_data.quantity,
        purchase_date=bondholder_data.purchase_date,
    )
    bond_dto = BondCreateDTO(
        series=bondholder_data.series,
        nominal_value=Decimal(bondholder_data.nominal_value),
        maturity_period=bondholder_data.maturity_period,
        initial_interest_rate=Decimal(bondholder_data.initial_interest_rate),
        first_interest_period=bondholder_data.first_interest_period,
        reference_rate_margin=Decimal(bondholder_data.reference_rate_margin),
    )
    response_dto = await use_case.execute(bondholder_dto, bond_dto)
    return BondHolderResponse(
        id=response_dto.id,
        quantity=response_dto.quantity,
        purchase_date=response_dto.purchase_date,
        last_update=response_dto.last_update,
        bond_id=response_dto.bond_id,
        series=response_dto.series,
        nominal_value=float(response_dto.nominal_value),
        maturity_period=response_dto.maturity_period,
        initial_interest_rate=float(response_dto.initial_interest_rate),
        first_interest_period=response_dto.first_interest_period,
        reference_rate_margin=float(response_dto.reference_rate_margin),
    )


@bond_router.get(
    "",
    response_model=list[BondHolderResponse],
    status_code=status.HTTP_200_OK,
    description="Get all bonds as combined bond and bond holder data",
)
async def get_all_bonds(
    user: CurrentUserDep,
    use_case: Annotated[BondHolderGetAllUseCase, Depends(bh_get_all_use_case)],
):
    return await use_case.execute(user=user)


@bond_router.get(
    "/{purchase_id}",
    response_model=BondHolderResponse,
    status_code=status.HTTP_200_OK,
    description="Get combined bond and bond holder data",
)
async def get_bond(
    user: CurrentUserDep,
    purchase_id: UUID,
    use_case: Annotated[BondHolderGetUseCase, Depends(bh_get_use_case)],
):
    dto = await use_case.execute(bondholder_id=purchase_id, user=user)
    return BondHolderResponse(
        id=dto.id,
        quantity=dto.quantity,
        purchase_date=dto.purchase_date,
        last_update=dto.last_update,
        bond_id=dto.bond_id,
        series=dto.series,
        nominal_value=float(dto.nominal_value),
        maturity_period=dto.maturity_period,
        initial_interest_rate=float(dto.initial_interest_rate),
        first_interest_period=dto.first_interest_period,
        reference_rate_margin=float(dto.reference_rate_margin),
    )


@bond_router.patch(
    "/{purchase_id}/quantity",
    response_model=BondHolderResponse,
    status_code=status.HTTP_200_OK,
    description="Change bond quantity in bond holder",
)
async def update_purchase_quantity(
    purchase_id: UUID,
    bond_data: BondHolderChangeRequest,
    use_case: Annotated[
        UpdateBondHolderQuantityUseCase, Depends(update_bh_quantity_use_case)
    ],
    user: CurrentUserDep,
):
    dto = BondHolderUpdateQuantityDTO(
        id=purchase_id,
        user=user,
        new_quantity=bond_data.new_quantity,
    )
    return await use_case.execute(dto=dto)


@bond_router.delete(
    "/{purchase_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete bond data",
)
async def delete_bond(
    purchase_id: UUID,
    user: CurrentUserDep,
    use_case: Annotated[BondHolderDeleteUseCase, Depends(bh_delete_use_case)],
):
    try:
        await use_case.execute(bondholder_id=purchase_id, user=user)
    except NotFoundError as _:
        pass  # Method is idempotent
