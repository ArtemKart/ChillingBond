from datetime import date
from uuid import uuid4

import pytest

from src.domain.entities.bondholder import BondHolder
from src.domain.exceptions import ValidationError


@pytest.fixture
async def bondholder() -> BondHolder:
    return BondHolder(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        quantity=100,
        purchase_date=date.today(),
    )


async def test_bondholder_add_quantity_err(bondholder: BondHolder) -> None:
    negative_quantity = -bondholder.quantity

    with pytest.raises(ValidationError, match="Amount must be positive"):
        await bondholder.add_quantity(negative_quantity)

    assert bondholder.quantity != negative_quantity


async def test_bondholder_add_quantity_happy_path(bondholder: BondHolder) -> None:
    before = bondholder.quantity
    amount = 44
    await bondholder.add_quantity(amount=amount)
    assert bondholder.quantity == before + amount


@pytest.mark.parametrize(
    "quantity, amount, expected_result",
    [
        (100, 44, 56),
        (100, 101, 0),
    ],
    ids=["amount less than quantity", "amount greater than quantity"],
)
async def test_bondholder_reduce_quantity(
    bondholder: BondHolder,
    quantity: int,
    amount: int,
    expected_result: int,
) -> None:
    bondholder.quantity = quantity
    await bondholder.reduce_quantity(amount=amount)
    assert bondholder.quantity == expected_result
