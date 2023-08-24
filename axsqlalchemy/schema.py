from uuid import UUID
from datetime import datetime
from pydantic import BaseModel as _BaseModel, root_validator

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


class IgnoreDeactiveSchema(BaseModel): 
    @root_validator(pre=True)
    def validate_value(cls, values):
        if 'is_active' in values and not values['is_active']:
            raise ValueError        
        return values
    
    class Config:
        skip_invalid_collections_items = True 

