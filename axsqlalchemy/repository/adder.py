from typing import Generic

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class AdderRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    async def add(self, obj: TIModel, autosave=True) -> TOModel:
        if type(obj) in (self.OSchema, self.Schema):
            obj = self.Schema.from_orm(obj)

        mobj = self.Model(**obj.dict())
        self.session.add(mobj)
        
        if autosave:
            await self.session.commit()

        return self.OSchema.from_orm(mobj)

