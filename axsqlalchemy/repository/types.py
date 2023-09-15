from typing import TypeVar
from pydantic import BaseModel
from axsqlalchemy.model import BaseTableAt


TDBModel = TypeVar("TDBModel", bound=BaseTableAt)
TIModel = TypeVar("TIModel", bound=BaseModel)
TOModel = TypeVar("TOModel", bound=BaseModel)

