from typing import Generic

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class AdderRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    async def add(self, obj: TIModel, autocommit=True) -> TOModel:
        if type(obj) in (self.OSchema, self.Schema):
            obj = self.Schema.from_orm(obj)

        mobj = self.Model(**obj.dict())
        self.session.add(mobj)
        
        if autocommit:
            await self.session.commit()

        return self.OSchema.from_orm(mobj)

