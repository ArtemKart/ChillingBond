from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.adapters.outbound.database.models import BondHolder as BondHolderModel
from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.adapters.outbound.repositories.bondholder import SQLAlchemyBondHolderRepository
from src.domain.entities.bondholder import BondHolder as BondHolderEntity


@pytest.fixture
def bondholder_model(bondholder_entity_mock: Mock) -> BondHolderModel:
    return BondHolderModel(
        id=bondholder_entity_mock.id,
        bond_id=bondholder_entity_mock.bond_id,
        user_id=bondholder_entity_mock.user_id,
        quantity=bondholder_entity_mock.quantity,
        purchase_date=bondholder_entity_mock.purchase_date,
        last_update=bondholder_entity_mock.last_update,
    )


@pytest.fixture
def repository(mock_session: AsyncMock) -> SQLAlchemyBondHolderRepository:
    return SQLAlchemyBondHolderRepository(mock_session)


async def test_get_one_success(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_model: BondHolderModel,
    bondholder_entity_mock: Mock,
) -> None:
    mock_session.get.return_value = bondholder_model

    result = await repository.get_one(bondholder_entity_mock.id)

    mock_session.get.assert_called_once_with(BondHolderModel, bondholder_entity_mock.id)
    assert result is not None
    assert result.id == bondholder_entity_mock.id
    assert result.bond_id == bondholder_entity_mock.bond_id
    assert result.user_id == bondholder_entity_mock.user_id
    assert result.quantity == bondholder_entity_mock.quantity


async def test_get_one_not_found(
    repository: SQLAlchemyBondHolderRepository, mock_session: AsyncMock
) -> None:
    bondholder_id = uuid4()
    mock_session.get.return_value = None

    result = await repository.get_one(bondholder_id)

    mock_session.get.assert_called_once_with(BondHolderModel, bondholder_id)
    assert result is None


async def test_get_all_success(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_model: BondHolderModel,
) -> None:
    user_id = uuid4()
    models = [
        bondholder_model,
        BondHolderModel(
            id=uuid4(),
            bond_id=uuid4(),
            user_id=user_id,
            quantity=200,
            purchase_date=datetime.now(),
            last_update=datetime.now(),
        ),
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = models
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    result = await repository.get_all(user_id)

    mock_session.execute.assert_called_once()
    assert len(result) == 2
    assert all(isinstance(item, BondHolderEntity) for item in result)


async def test_get_all_empty_result(
    repository: SQLAlchemyBondHolderRepository, mock_session: AsyncMock
) -> None:
    user_id = uuid4()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    result = await repository.get_all(user_id)

    mock_session.execute.assert_called_once()
    assert result == []


async def test_write_success(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    result = await repository.write(bondholder_entity_mock)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.id == bondholder_entity_mock.id
    assert result.bond_id == bondholder_entity_mock.bond_id
    assert result.user_id == bondholder_entity_mock.user_id


async def test_write_integrity_error(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    mock_session.commit.side_effect = IntegrityError("", "", "")

    with pytest.raises(
        SQLAlchemyRepositoryError,
        match="BondHolder already exists or constraint violated",
    ):
        await repository.write(bondholder_entity_mock)
    mock_session.rollback.assert_called_once()


async def test_write_sqlalchemy_error(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(
        SQLAlchemyRepositoryError, match="Failed to save BondHolder object"
    ):
        await repository.write(bondholder_entity_mock)
    mock_session.rollback.assert_called_once()


async def test_update_success(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity_mock: Mock,
    bondholder_model: BondHolderModel,
) -> None:
    mock_session.get.return_value = bondholder_model
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    bondholder_entity_mock.quantity = 200
    bondholder_entity_mock.last_update = datetime.now()

    result = await repository.update(bondholder_entity_mock)

    mock_session.get.assert_called_once_with(BondHolderModel, bondholder_entity_mock.id)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.id == bondholder_entity_mock.id


async def test_update_sqlalchemy_error(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    mock_session.get.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(
        SQLAlchemyRepositoryError, match="Failed to update BondHolder object"
    ):
        await repository.update(bondholder_entity_mock)
    mock_session.rollback.assert_called_once()


async def test_update_model_not_found(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity_mock: Mock,
) -> None:
    mock_session.get.return_value = None

    with pytest.raises(
        SQLAlchemyRepositoryError, match="BondHolder not found"
    ):
        await repository.update(bondholder_entity_mock)


async def test_to_entity_conversion(
    repository: SQLAlchemyBondHolderRepository, bondholder_model: BondHolderModel
) -> None:
    result = repository._to_entity(bondholder_model)

    assert isinstance(result, BondHolderEntity)
    assert result.id == bondholder_model.id
    assert result.bond_id == bondholder_model.bond_id
    assert result.user_id == bondholder_model.user_id
    assert result.quantity == bondholder_model.quantity
    assert result.purchase_date == bondholder_model.purchase_date
    assert result.last_update == bondholder_model.last_update


async def test_to_model_conversion(
    repository: SQLAlchemyBondHolderRepository, bondholder_entity_mock: Mock
) -> None:
    result = repository._to_model(bondholder_entity_mock)

    assert isinstance(result, BondHolderModel)
    assert result.id == bondholder_entity_mock.id
    assert result.bond_id == bondholder_entity_mock.bond_id
    assert result.user_id == bondholder_entity_mock.user_id
    assert result.quantity == bondholder_entity_mock.quantity
    assert result.purchase_date == bondholder_entity_mock.purchase_date
    assert result.last_update == bondholder_entity_mock.last_update


async def test_update_model(
    repository: SQLAlchemyBondHolderRepository, bondholder_model: BondHolderModel
) -> None:
    new_entity = BondHolderEntity(
        id=bondholder_model.id,
        bond_id=uuid4(),
        user_id=uuid4(),
        quantity=300,
        purchase_date=datetime.now(),
        last_update=datetime.now(),
    )

    repository._update_model(bondholder_model, new_entity)

    assert bondholder_model.bond_id == new_entity.bond_id
    assert bondholder_model.user_id == new_entity.user_id
    assert bondholder_model.quantity == 300
    assert bondholder_model.purchase_date == new_entity.purchase_date
    assert bondholder_model.last_update == new_entity.last_update


async def test_get_all_with_multiple_users(
    repository: SQLAlchemyBondHolderRepository, mock_session: AsyncMock
) -> None:
    target_user_id = uuid4()

    target_models = [
        BondHolderModel(
            id=uuid4(),
            bond_id=uuid4(),
            user_id=target_user_id,
            quantity=100,
            purchase_date=datetime.now(),
            last_update=datetime.now(),
        ),
        BondHolderModel(
            id=uuid4(),
            bond_id=uuid4(),
            user_id=target_user_id,
            quantity=200,
            purchase_date=datetime.now(),
            last_update=datetime.now(),
        ),
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = target_models
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    result = await repository.get_all(target_user_id)

    assert len(result) == 2
    assert all(holder.user_id == target_user_id for holder in result)


async def test_delete_existing_bondholder(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_model: BondHolderModel,
) -> None:
    bondholder_id = uuid4()
    mock_session.get.return_value = bondholder_model

    await repository.delete(bondholder_id)

    mock_session.get.assert_called_once_with(BondHolderModel, bondholder_id)
    mock_session.delete.assert_called_once_with(bondholder_model)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_delete_nonexistent_bondholder(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    mock_session.get.return_value = None

    await repository.delete(bondholder_id)

    mock_session.get.assert_called_once_with(BondHolderModel, bondholder_id)
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_delete_sqlalchemy_error_on_get(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
) -> None:
    bondholder_id = uuid4()
    mock_session.get.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to delete bondholder"):
        await repository.delete(bondholder_id)

    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_sqlalchemy_error_on_delete(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_model: BondHolderModel,
) -> None:
    bondholder_id = uuid4()
    mock_session.get.return_value = bondholder_model
    mock_session.delete.side_effect = SQLAlchemyError("Delete failed")

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to delete bondholder"):
        await repository.delete(bondholder_id)

    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_sqlalchemy_error_on_commit(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_model: BondHolderModel,
) -> None:
    bondholder_id = uuid4()
    mock_session.get.return_value = bondholder_model
    mock_session.commit.side_effect = SQLAlchemyError("Commit failed")

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to delete bondholder"):
        await repository.delete(bondholder_id)

    mock_session.rollback.assert_called_once()


async def test_count_by_bond_id_returns_count(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
) -> None:
    bond_id = uuid4()
    expected_count = 5

    mock_result = Mock()
    mock_result.scalar_one.return_value = expected_count
    mock_session.execute.return_value = mock_result

    result = await repository.count_by_bond_id(bond_id)

    assert result == expected_count
    mock_session.execute.assert_called_once()
    mock_result.scalar_one.assert_called_once()


async def test_count_by_bond_id_returns_zero(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
) -> None:
    bond_id = uuid4()

    mock_result = Mock()
    mock_result.scalar_one.return_value = 0
    mock_session.execute.return_value = mock_result

    result = await repository.count_by_bond_id(bond_id)

    assert result == 0
    mock_session.execute.assert_called_once()


async def test_count_by_bond_id_verifies_query_structure(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
) -> None:
    bond_id = uuid4()

    mock_result = Mock()
    mock_result.scalar_one.return_value = 3
    mock_session.execute.return_value = mock_result

    await repository.count_by_bond_id(bond_id)

    call_args = mock_session.execute.call_args[0][0]
    assert "count" in str(call_args).lower()
