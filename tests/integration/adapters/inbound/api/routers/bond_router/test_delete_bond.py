from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.adapters.outbound.database.models import BondHolder as BondholderModel
from src.adapters.outbound.database.models import Bond as BondModel
from src.adapters.outbound.database.models import User as UserModel


async def _check_bondholder_exists(
    session: AsyncSession,
    bondholder_id: UUID,
) -> bool:
    bondholder = await session.get(BondholderModel, bondholder_id)
    return bondholder is not None


async def test_delete_bond(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    t_session: AsyncSession,
) -> None:
    await _check_bondholder_exists(t_session, t_bondholder.id)

    r = await client.delete(f"api/bonds/{t_bondholder.id}")

    assert r.status_code == status.HTTP_204_NO_CONTENT

    bondholder = await t_session.get(BondholderModel, t_bondholder.id)
    assert bondholder is None


async def test_keep_bond(
    client: AsyncClient,
    t_bondholder: BondholderModel,
    t_session: AsyncSession,
) -> None:
    await _check_bondholder_exists(t_session, t_bondholder.id)

    bond_id = t_bondholder.bond_id
    bond = await t_session.get(BondModel, bond_id)
    assert bond

    second_bh = BondholderModel(
        id=uuid4(),
        bond_id=bond_id,
        user_id=t_bondholder.user_id,
        quantity=50,
        purchase_date=t_bondholder.purchase_date,
        last_update=None,
    )
    t_session.add(second_bh)
    await t_session.commit()
    await t_session.refresh(second_bh)

    r = await client.delete(f"api/bonds/{t_bondholder.id}")

    assert r.status_code == status.HTTP_204_NO_CONTENT

    bond = await t_session.get(BondModel, bond_id)
    assert bond


async def test_bondholder_not_found_idempotent(
    client: AsyncClient,
    t_session: AsyncSession,
) -> None:
    non_existent_id = uuid4()
    bondholder = await t_session.get(BondholderModel, non_existent_id)
    assert not bondholder

    r = await client.delete(f"api/bonds/{non_existent_id}")
    assert r.status_code == status.HTTP_204_NO_CONTENT


async def test_authorization_error(
    t_session: AsyncSession,
    client: AsyncClient,
    t_bond: BondModel,
) -> None:
    from datetime import date

    user = UserModel(
        id=uuid4(),
        email="test_user@mail.com",
        password="hashed_password",
        name="Test User",
    )
    t_session.add(user)
    await t_session.commit()
    await t_session.refresh(user)

    bondholder = BondholderModel(
        id=uuid4(),
        bond_id=t_bond.id,
        user_id=user.id,
        quantity=10,
        purchase_date=date.today(),
        last_update=None,
    )
    t_session.add(bondholder)
    await t_session.commit()
    await t_session.refresh(bondholder)

    r = await client.delete(f"api/bonds/{bondholder.id}")

    assert r.status_code == status.HTTP_403_FORBIDDEN
    assert r.json()["detail"] == "Permission denied"
