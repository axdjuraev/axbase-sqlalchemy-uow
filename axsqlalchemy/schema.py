from uuid import UUID
from datetime import datetime
from pydantic import Field, root_validator
from axabc.db import BaseSchema as _BaseSchema


class BaseModelAt(_BaseSchema):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None


class BaseModel(BaseModelAt):
    class Config:
        orm_mode = True


class BaseModelUUID(BaseModel):
    id: UUID | None = None


class BaseModelInt(BaseModel):
    id: int | None = None


class IgnoreDeactiveSchema(BaseModel): 
    @root_validator(pre=True)
    def validate_value(cls, values):
        if 'is_active' in values and not values['is_active']:
            raise ValueError        
        return values
    
    class Config:
        skip_invalid_collections_items = True 

