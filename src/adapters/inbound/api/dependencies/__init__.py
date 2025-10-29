from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.config import get_config, Config
from src.adapters.outbound.database.engine import get_session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
ConfigDep = Annotated[Config, Depends(get_config)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")
