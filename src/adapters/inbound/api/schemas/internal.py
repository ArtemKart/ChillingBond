from pydantic import BaseModel


class UpdateReferenceResponse(BaseModel):
    status: str
    rate_changed: str
    message: str
