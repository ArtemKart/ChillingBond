import bcrypt
from src.domain.ports.services.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self, rounds: int = 12) -> None:
        self.rounds = rounds

    def hash(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=self.rounds)
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
