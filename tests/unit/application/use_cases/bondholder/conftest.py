from uuid import uuid4

import pytest

from src.application.dto.user import UserDTO


@pytest.fixture
def user_dto() -> UserDTO:
    return UserDTO(id=uuid4(), email="test_email@test_email", name="test_name")
