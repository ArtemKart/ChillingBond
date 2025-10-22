from typing import Annotated

from fastapi import Depends

from src.adapters.inbound.api.dependencies import ConfigDep
from src.adapters.outbound.security.bcrypt_hasher import BcryptPasswordHasher
from src.adapters.outbound.security.jwt_token_handler import JWTTokenHandler


def hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


def token_handler(config: ConfigDep) -> JWTTokenHandler:
    return JWTTokenHandler(config=config)


HasherDep = Annotated[BcryptPasswordHasher, Depends(hasher)]
TokenHandlerDep = Annotated[JWTTokenHandler, Depends(token_handler)]
