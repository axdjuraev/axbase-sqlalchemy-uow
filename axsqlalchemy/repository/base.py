from typing import Any, Generic, Iterable, Type
from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from axabc.db.async_repository import AbstractAsyncRepository

from .types import TIModel, TOModel, TDBModel


class BaseRepoCreator(AbstractAsyncRepository, Generic[TDBModel, TIModel, TOModel]):
    Model: Type[TDBModel]
    Schema: Type[TIModel]
    OSchema: Type[TOModel]

    _default_filters: tuple = tuple()
    ids: tuple[Column]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._setup_ids()

    def _get_filters(self, ids = tuple(), columns: Iterable[Any] = tuple(), use_defaults: bool = True, extra_filters: Iterable[Any] = tuple()) -> tuple[Any]:
        if not ids:
            return (*self._default_filters, *extra_filters) or (True, )

        filters = [*extra_filters]
        columns = columns or self.ids
        ids = self._get_obj_ids(ids[-1], columns) if self._is_obj(ids[-1]) else ids 

        if columns is not None and ids:
            for colum, value in zip(columns, ids):
                filters.append(colum == value)
        
        if use_defaults:
            filters.extend(self._default_filters)

        return tuple(filters) or (True, )

    def _get_obj_ids(self, obj: TIModel, columns) -> tuple[Any]:
        if not columns:
            return tuple()

        ids = []
        for column in columns:
            ids.append(getattr(obj, column.name))

        return tuple(ids)

    def _is_obj(self, obj):
        return isinstance(obj, self.Schema) or isinstance(obj, self.OSchema)

    def _setup_ids(self):
        if hasattr(self, 'ids'):
            return

        ids = []
        for constraint in self.Model.__table__.constraints:
            if type(constraint) is PrimaryKeyConstraint:
                for column in constraint.columns:
                    ids.append(column)

        self.ids = tuple(ids)

