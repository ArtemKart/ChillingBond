import pytest
from datetime import datetime, date
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.adapters.exceptions import SQLAlchemyRepositoryError
from src.adapters.outbound.database.models import BondHolder as BondHolderModel
from src.adapters.outbound.repositories.bondholder import SQLAlchemyBondHolderRepository
from src.domain.entities.bondholder import BondHolder as BondHolderEntity


@pytest_asyncio.fixture
def bondholder_entity() -> BondHolderEntity:
    return BondHolderEntity(
        id=uuid4(),
        bond_id=uuid4(),
        user_id=uuid4(),
        quantity=100,
        purchase_date=date.today(),
        last_update=datetime.now(),
    )


@pytest_asyncio.fixture
def bondholder_model(bondholder_entity: BondHolderEntity) -> BondHolderModel:
    return BondHolderModel(
        id=bondholder_entity.id,
        bond_id=bondholder_entity.bond_id,
        user_id=bondholder_entity.user_id,
        quantity=bondholder_entity.quantity,
        purchase_date=bondholder_entity.purchase_date,
        last_update=bondholder_entity.last_update,
    )


@pytest_asyncio.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest_asyncio.fixture
def repository(mock_session: AsyncMock) -> SQLAlchemyBondHolderRepository:
    return SQLAlchemyBondHolderRepository(mock_session)


async def test_get_one_success(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_model: BondHolderModel,
    bondholder_entity: BondHolderEntity,
) -> None:
    mock_session.get.return_value = bondholder_model

    result = await repository.get_one(bondholder_entity.id)

    mock_session.get.assert_called_once_with(BondHolderModel, bondholder_entity.id)
    assert result is not None
    assert result.id == bondholder_entity.id
    assert result.bond_id == bondholder_entity.bond_id
    assert result.user_id == bondholder_entity.user_id
    assert result.quantity == bondholder_entity.quantity


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
    bondholder_entity: BondHolderEntity,
) -> None:
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    result = await repository.write(bondholder_entity)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.id == bondholder_entity.id
    assert result.bond_id == bondholder_entity.bond_id
    assert result.user_id == bondholder_entity.user_id


async def test_write_integrity_error(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity: BondHolderEntity,
) -> None:
    mock_session.commit.side_effect = IntegrityError("", "", "")

    with pytest.raises(
        SQLAlchemyRepositoryError,
        match="BondHolder already exists or constraint violated",
    ):
        await repository.write(bondholder_entity)
    mock_session.rollback.assert_called_once()


async def test_write_sqlalchemy_error(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity: BondHolderEntity,
) -> None:
    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(
        SQLAlchemyRepositoryError, match="Failed to save BondHolder object"
    ):
        await repository.write(bondholder_entity)
    mock_session.rollback.assert_called_once()


async def test_update_success(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity: BondHolderEntity,
    bondholder_model: BondHolderModel,
) -> None:
    mock_session.get.return_value = bondholder_model
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    bondholder_entity.quantity = 200
    bondholder_entity.last_update = datetime.now()

    result = await repository.update(bondholder_entity)

    mock_session.get.assert_called_once_with(BondHolderModel, bondholder_entity.id)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.id == bondholder_entity.id


async def test_update_sqlalchemy_error(
    repository: SQLAlchemyBondHolderRepository,
    mock_session: AsyncMock,
    bondholder_entity: BondHolderEntity,
) -> None:
    mock_session.get.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(
        SQLAlchemyRepositoryError, match="Failed to update BondHolder object"
    ):
        await repository.update(bondholder_entity)
    mock_session.rollback.assert_called_once()


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
    repository: SQLAlchemyBondHolderRepository, bondholder_entity: BondHolderEntity
) -> None:
    result = repository._to_model(bondholder_entity)

    # Assert
    assert isinstance(result, BondHolderModel)
    assert result.id == bondholder_entity.id
    assert result.bond_id == bondholder_entity.bond_id
    assert result.user_id == bondholder_entity.user_id
    assert result.quantity == bondholder_entity.quantity
    assert result.purchase_date == bondholder_entity.purchase_date
    assert result.last_update == bondholder_entity.last_update


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
