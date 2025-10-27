from abc import ABC, abstractmethod

from src.domain.entities.token import Token


class TokenHandler(ABC):
    @abstractmethod
    def create_token(self, subject: str) -> Token:
        pass

    @abstractmethod
    def read_token(self, subject: str) -> str:
        pass
