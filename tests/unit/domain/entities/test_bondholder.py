from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio

from src.domain.entities.bondholder import BondHolder as BondHolderEntity
from src.domain.exceptions import ValidationError


@pytest_asyncio.fixture
def local_bondholder() -> BondHolderEntity:
    return BondHolderEntity(
        id=uuid4(),
        bond_id=uuid4(),
        user_id = uuid4(),
        quantity = 100,
        purchase_date = date.today(),
    )

async def test_bondholder_add_quantity_err(local_bondholder: BondHolderEntity) -> None:
    negative_quantity = -local_bondholder.quantity

    with pytest.raises(ValidationError, match="Amount must be positive"):
        local_bondholder.add_quantity(negative_quantity)

    assert local_bondholder.quantity != negative_quantity


async def test_bondholder_add_quantity_happy_path(local_bondholder: BondHolderEntity) -> None:
    before = local_bondholder.quantity
    amount = 44
    local_bondholder.add_quantity(amount=amount)
    assert local_bondholder.quantity == before + amount


@pytest.mark.parametrize(
    "quantity, amount, expected_result",
    [
        (100, 44, 56),
        (100, 101, 0),
    ],
    ids=["amount less than quantity", "amount greater than quantity"],
)
async def test_bondholder_reduce_quantity(
    local_bondholder: BondHolderEntity,
    quantity: int,
    amount: int,
    expected_result: int,
) -> None:
    local_bondholder.quantity = quantity
    local_bondholder.reduce_quantity(amount=amount)
    assert local_bondholder.quantity == expected_result
