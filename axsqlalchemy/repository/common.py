from typing import Generic

from .types import TIModel, TOModel, TDBModel
from .adder import AdderRepo
from .getter import GetterRepo
from .updateter import UpdateterRepo
from .status_updater import StatusUpdaterRepo
from .deleter import DeleterRepo
from .paginated_all_getter import PaginatedAllGetterRepo


class BaseRepository(
	AdderRepo[TDBModel, TIModel, TOModel],
	GetterRepo[TDBModel, TIModel, TOModel],
	UpdateterRepo[TDBModel, TIModel, TOModel],
	StatusUpdaterRepo[TDBModel, TIModel, TOModel],
	DeleterRepo[TDBModel, TIModel, TOModel],
	PaginatedAllGetterRepo[TDBModel, TIModel, TOModel],
    Generic[TDBModel, TIModel, TOModel],
):
    __abstract__ = True 

    def __init_subclass__(cls) -> None:
        if not cls.__dict__.get('__abstract__'):
            types = getattr(cls, "__orig_bases__")[0].__args__
            cls.Model, cls.Schema, cls.OSchema = types

