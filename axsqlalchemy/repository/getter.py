from .base import BaseRepoCreator



class GetterRepo(BaseRepoCreator):
    async def get(self, *ids: Any, filters: Union[tuple, None] = None) -> Union[TOModel, None]:
        filters = self.__get_filters(ids, extra_filters=filters, use_defaults=False)

        if self.Model.ids is None:
            raise NotImplementedError

        obj = (
            (
                await self.session.execute(
                    select(self.Model)
                    .where(and_(*filters))
                    .order_by(self.Model.created_at.desc()),
                )
            )
            .scalars()
            .first()
        )

        if obj:
            return self.OSchema.from_orm(obj)

