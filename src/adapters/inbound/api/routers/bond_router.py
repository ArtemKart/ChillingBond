from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.adapters.inbound.api.dependencies.bond_use_cases_deps import (
    bh_delete_use_case,
    bh_get_all_use_case,
    bh_get_use_case,
    bond_add_to_bh_use_case,
    bond_update_use_case,
    create_bondholder_use_case,
)
from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.adapters.inbound.api.schemas.bond import (
    BondUpdateRequest,
    BondUpdateResponse,
    EmptyBondUpdateResponse,
)
from src.adapters.inbound.api.schemas.bondholder import (
    BondHolderChangeRequest,
    BondHolderCreateRequest,
    BondHolderResponse,
)
from src.application.dto.bond import BondCreateDTO, BondUpdateDTO
from src.application.dto.bondholder import (
    BondHolderChangeQuantityDTO,
    BondHolderCreateDTO,
)
from src.application.use_cases.bond_update import BondUpdateUseCase
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
async def change_purchase_quantity(
    purchase_id: UUID,
    bond_data: BondHolderChangeRequest,
    use_case: Annotated[
        ChangeBondHolderQuantityUseCase, Depends(bond_add_to_bh_use_case)
    ],
    user_id: Annotated[UUID, Depends(current_user)],
):
    dto = BondHolderChangeQuantityDTO(
        id=purchase_id,
        user_id=user_id,
        new_quantity=bond_data.new_quantity,
    )
    return await use_case.execute(dto=dto)


@bond_router.put(
    "/{purchase_id}/specification",
    dependencies=[Depends(current_user)],
    status_code=status.HTTP_200_OK,
    description="Update bond specification data",
)
async def update_bond(
    purchase_id: UUID,
    bond_data: BondUpdateRequest,
    use_case: Annotated[BondUpdateUseCase, Depends(bond_update_use_case)],
) -> BondUpdateResponse | EmptyBondUpdateResponse:
    if not bond_data.model_dump(exclude_none=True):
        return EmptyBondUpdateResponse()
    dto = BondUpdateDTO(
        nominal_value=Decimal(bond_data.nominal_value)
        if bond_data.nominal_value
        else None,
        series=bond_data.series,
        maturity_period=bond_data.maturity_period,
        initial_interest_rate=Decimal(bond_data.initial_interest_rate)
        if bond_data.initial_interest_rate
        else None,
        first_interest_period=bond_data.first_interest_period,
        reference_rate_margin=Decimal(bond_data.reference_rate_margin)
        if bond_data.reference_rate_margin
        else None,
    )
    return await use_case.execute(dto=dto, bond_id=purchase_id)  # type: ignore [return-value]


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
        pass  # Method is idempotent
