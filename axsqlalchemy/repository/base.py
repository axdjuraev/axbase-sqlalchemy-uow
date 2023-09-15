from abc import ABC
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

    def _get_filters(self, *ids, columns: Iterable[Any] = tuple(), use_defaults: bool = True, extra_filters: Iterable[Any] = tuple()) -> tuple[Any]:
        if not ids:
            return (*self._default_filters, *extra_filters) or (True, )

        filters = [*extra_filters]
        columns = columns or self.ids

        if columns is not None:
            for colum, value in zip(columns, ids):
                filters.append(colum == value)
        
        if use_defaults:
            filters.extend(self._default_filters)

        return tuple(filters) or (True, )

    def _setup_ids(self):
        if hasattr(self, 'ids'):
            return

        ids = []
        for constraint in self.Model.__table__.constraints:
            if type(constraint) is PrimaryKeyConstraint:
                for column in constraint.columns:
                    ids.append(column)

        self.ids = tuple(ids)

