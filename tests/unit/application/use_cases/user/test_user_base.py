from uuid import uuid4
from src.application.use_cases.user.base import UserBaseUseCase
from src.domain.entities.user import User as UserEntity


async def test_to_dto() -> None:
    userbase_use_case = UserBaseUseCase()
    user = UserEntity(id=uuid4(), email="test@example.com", name="Test User", hashed_password="hashed_password")
    dto = userbase_use_case.to_dto(user)
    assert dto.id == user.id
    assert dto.email == user.email
    assert dto.name == user.name
    
