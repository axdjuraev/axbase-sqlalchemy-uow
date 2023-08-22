from functools import wraps
from typing import List, Union


def filter_none_params(include: Union[List[str], None] = None, exclude: Union[List[str], None] = None):
    def inner_wrapper(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            filters = []
            exclude_ = ['filters', *(exclude or [])]
            if include is not None:
                for param in include:
                    type_ = f.__annotations__.get(param)
                    value = kwargs.get(param) or f.__kwdefaults__.get(param)
                    if (type_ is not None and value is not None and param not in exclude_):
                        filters.append(type_ == value)
            else:
                for param, type_ in f.__annotations__.items():
                    value = kwargs.get(param) or f.__kwdefaults__.get(param)
                    if value is not None and param not in exclude_:
                        filters.append(type_ == value)
            return await f(*args, filters=filters, **kwargs)

        return wrapper

    return inner_wrapper

