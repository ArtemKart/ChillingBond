from abc import ABC, abstractmethod

from src.domain.entities.token import Token


class TokenHandler(ABC):
    @abstractmethod
    async def create_token(self, subject: str) -> Token:
        pass

    @abstractmethod
    async def read_token(self, subject: str) -> str:
        pass
