from typing import Generic, Iterable, Optional

from .types import TIModel, TOModel, TDBModel

from .adder import AdderRepo
from .getter import GetterRepo
from .updateter import UpdateterRepo



class BaseRepository(
    AbstractAsyncRepository
):
    def __init_subclass__(cls) -> None:
        types = getattr(cls, "__orig_bases__")[0].__args__
        cls.Model, cls.Schema, cls.OSchema = types

    async def delete(self, *ids, filters: Union[tuple, None] = None) -> None:
        filters = self.__get_filters(ids, extra_filters=filters, use_defaults=False)
        await self.session.execute(delete(self.Model).where(*filters))


