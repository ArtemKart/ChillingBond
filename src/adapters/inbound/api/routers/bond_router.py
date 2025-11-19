from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
    bond_add_to_bh_use_case,
    create_bondholder_use_case,
    bond_update_use_case,
    bh_get_use_case,
    bh_get_all_use_case, bh_delete_use_case,
)
from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.adapters.inbound.api.schemas.bond import BondUpdateRequest, BondUpdateResponse
from src.adapters.inbound.api.schemas.bondholder import (
    BondHolderResponse,
    BondHolderChangeRequest,
    BondHolderCreateRequest,
)
from src.application.dto.bond import BondCreateDTO, BondUpdateDTO
from src.application.dto.bondholder import (
    BondHolderCreateDTO,
    BondHolderChangeQuantityDTO,
)
from src.application.use_cases.bondholder.bondholder_add import (
    BondAddToBondHolderUseCase,
)
from src.application.use_cases.bondholder.bondholder_create import (
    BondHolderCreateUseCase,
)
from src.application.use_cases.bondholder.bondholder_delete import BondHolderDeleteUseCase
from src.application.use_cases.bondholder.bondholder_get import (
    BondHolderGetUseCase,
    BondHolderGetAllUseCase,
)
from src.application.use_cases.bond_update import BondUpdateUseCase
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
    user_id: Annotated[UUID, Depends(current_user)],
    use_case: Annotated[BondHolderCreateUseCase, Depends(create_bondholder_use_case)],
):
    bondholder_dto = BondHolderCreateDTO(
        user_id=user_id,
        quantity=bondholder_data.quantity,
        purchase_date=bondholder_data.purchase_date,
    )
    bond_dto = BondCreateDTO(
        series=bondholder_data.series,
        nominal_value=bondholder_data.nominal_value,
        maturity_period=bondholder_data.maturity_period,
        initial_interest_rate=bondholder_data.initial_interest_rate,
        first_interest_period=bondholder_data.first_interest_period,
        reference_rate_margin=bondholder_data.reference_rate_margin,
    )
    response_dto = await use_case.execute(bondholder_dto, bond_dto)
    return BondHolderResponse(
        id=response_dto.id,
        quantity=response_dto.quantity,
        purchase_date=response_dto.purchase_date,
        last_update=response_dto.last_update,
        bond_id=response_dto.bond_id,
        series=response_dto.series,
        nominal_value=response_dto.nominal_value,
        maturity_period=response_dto.maturity_period,
        initial_interest_rate=response_dto.initial_interest_rate,
        first_interest_period=response_dto.first_interest_period,
        reference_rate_margin=response_dto.reference_rate_margin,
    )


@bond_router.get(
    "",
    response_model=list[BondHolderResponse],
    status_code=status.HTTP_200_OK,
    description="Get all bonds as combined bond and bond holder data",
)
async def get_all_bonds(
    user_id: Annotated[UUID, Depends(current_user)],
    use_case: Annotated[BondHolderGetAllUseCase, Depends(bh_get_all_use_case)],
):
    return await use_case.execute(user_id=user_id)


@bond_router.get(
    "/{purchase_id}",
    response_model=BondHolderResponse,
    status_code=status.HTTP_200_OK,
    description="Get combined bond and bond holder data",
)
async def get_bond(
    user_id: Annotated[UUID, Depends(current_user)],
    purchase_id: UUID,
    use_case: Annotated[BondHolderGetUseCase, Depends(bh_get_use_case)],
):
    dto = await use_case.execute(bondholder_id=purchase_id, user_id=user_id)
    return BondHolderResponse(
        id=dto.id,
        quantity=dto.quantity,
        purchase_date=dto.purchase_date,
        last_update=dto.last_update,
        bond_id=dto.bond_id,
        series=dto.series,
        nominal_value=dto.nominal_value,
        maturity_period=dto.maturity_period,
        initial_interest_rate=dto.initial_interest_rate,
        first_interest_period=dto.first_interest_period,
        reference_rate_margin=dto.reference_rate_margin,
    )


@bond_router.patch(
    "/{purchase_id}/add",
    response_model=BondHolderResponse,
    status_code=status.HTTP_200_OK,
    description="Change bond quantity in bond holder",
)
async def add_to_bond_purchase(
    purchase_id: UUID,
    bond_data: BondHolderChangeRequest,
    use_case: Annotated[BondAddToBondHolderUseCase, Depends(bond_add_to_bh_use_case)],
    user_id: Annotated[UUID, Depends(current_user)],
):
    dto = BondHolderChangeQuantityDTO(
        id=purchase_id,
        user_id=user_id,
        quantity=bond_data.quantity,
        is_positive=bond_data.is_positive,
    )
    return await use_case.execute(dto=dto)


@bond_router.put(
    "/{purchase_id}/specification",
    response_model=BondUpdateResponse,
    dependencies=[Depends(current_user)],
    status_code=status.HTTP_200_OK,
    description="Update bond specification data",
)
async def update_bond(
    purchase_id: UUID,
    bond_data: BondUpdateRequest,
    use_case: Annotated[BondUpdateUseCase, Depends(bond_update_use_case)],
):
    dto = BondUpdateDTO(
        nominal_value=bond_data.nominal_value,
        series=bond_data.series,
        maturity_period=bond_data.maturity_period,
        initial_interest_rate=bond_data.initial_interest_rate,
        first_interest_period=bond_data.first_interest_period,
        reference_rate_margin=bond_data.reference_rate_margin,
    )
    return await use_case.execute(dto=dto, bond_id=purchase_id)


@bond_router.delete(
    "/{purchase_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete bond data",
)
async def delete_bond(
    purchase_id: UUID,
    user_id: Annotated[UUID, Depends(current_user)],
    use_case: Annotated[BondHolderDeleteUseCase, Depends(bh_delete_use_case)],
):
    try:
        await use_case.execute(bondholder_id=purchase_id, user_id=user_id)
    except NotFoundError as _:
        pass # Method is idempotent
