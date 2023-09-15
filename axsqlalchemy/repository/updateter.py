from sqlalchemy import update
from typing import Generic, Iterable, Union

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class UpdateterRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    async def update(self, obj: Union[TIModel, TOModel], filters: Iterable = tuple()) -> TIModel:
        if type(obj) in (self.OSchema, self.Schema):
            obj = self.Schema.from_orm(obj)

        filters = self._get_filters((obj,), extra_filters=filters, use_defaults=False)

        await self.session.execute(
            update(self.Model)
            .where(*filters)
            .values(**obj.dict()),
        )

        return self.Schema.from_orm(obj)

