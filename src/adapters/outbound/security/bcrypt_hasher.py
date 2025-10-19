import bcrypt
from src.domain.ports.services.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    async def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    async def verify(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
