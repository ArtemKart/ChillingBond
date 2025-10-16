from typing import Final

from fastapi import FastAPI

from src.adapters.inbound.api.routers.bond_router import bond_router
from src.adapters.inbound.api.routers.user_router import user_router

app: Final = FastAPI()


app.include_router(user_router)
app.include_router(bond_router)
