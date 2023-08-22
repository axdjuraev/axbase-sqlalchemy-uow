from uuid import UUID
from datetime import datetime
from pydantic import BaseModel as _BaseModel

class BaseModelAt(_BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BaseModel(BaseModelAt):
    class Config:
        orm_mode = True


class BaseModelUUID(BaseModel):
    id: UUID | None = None


class BaseModelInt(BaseModel):
    id: int | None = None

