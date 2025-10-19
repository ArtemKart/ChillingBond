from uuid import UUID

from fastapi import Depends, HTTPException
from jwt import PyJWTError
from starlette import status

from src.adapters.inbound.api.dependencies import oauth2_scheme
from src.adapters.inbound.api.dependencies.security_deps import TokenHandlerDep


async def get_current_user(
    token_handler: TokenHandlerDep,
    token: str = Depends(oauth2_scheme),
) -> UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = await token_handler.read_token(subject=token)
        if user_id is None:
            raise credentials_exception
        return UUID(user_id)
    except (PyJWTError, ValueError) as e:
        raise credentials_exception from e
