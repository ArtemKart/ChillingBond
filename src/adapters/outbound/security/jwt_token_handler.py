from datetime import timedelta, datetime, timezone
from typing import Any

import jwt

from src.adapters.config import Config
from src.domain.entities.token import Token
from src.domain.ports.services.token_handler import TokenHandler


class JWTTokenHandler(TokenHandler):
    def __init__(self, config: Config, expire_delta: timedelta | None = None) -> None:
        self.expire_delta = expire_delta if expire_delta else timedelta(hours=1)
        self._config = config

    def create_token(self, subject: str) -> Token:
        to_encode = self._to_encode(subject)
        token = jwt.encode(
            to_encode,
            self._config.SECRET_KEY,
            self._config.ALGORITHM,
        )
        return Token(
            token=token,
            type="bearer",
        )

    def read_token(self, subject: str) -> str:
        payload = jwt.decode(
            subject,
            self._config.SECRET_KEY,
            algorithms=[self._config.ALGORITHM],
            options={"verify_exp": True},
        )
        return payload.get("sub")

    def _to_encode(self, subject: str) -> dict[str, Any]:
        return {
            "exp": datetime.now(timezone.utc) + self.expire_delta,
            "sub": str(subject),
        }
