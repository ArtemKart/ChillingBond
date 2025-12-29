from typing import Annotated

from fastapi import Depends, Header, HTTPException
from starlette import status

from src.adapters.config import get_config
from src.adapters.inbound.api.dependencies import ConfigDep
from src.adapters.outbound.security.bcrypt_hasher import BcryptPasswordHasher
from src.adapters.outbound.security.jwt_token_handler import JWTTokenHandler


def hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


def token_handler(config: ConfigDep) -> JWTTokenHandler:
    return JWTTokenHandler(config=config)


async def verify_internal_api_key(x_api_key: str = Header(...)) -> None:
    config = get_config()
    if x_api_key != config.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )


HasherDep = Annotated[BcryptPasswordHasher, Depends(hasher)]
TokenHandlerDep = Annotated[JWTTokenHandler, Depends(token_handler)]
