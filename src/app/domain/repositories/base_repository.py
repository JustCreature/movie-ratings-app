from enum import Enum
from typing import Any, Callable, Generic, Type, TypeVar
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import asc, desc, func
from sqlalchemy.engine import Result  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ClauseElement, ClauseList, ColumnElement
from sqlalchemy import select, and_

T_Model = TypeVar("T_Model", bound="BaseDBModel")
T_Schema = TypeVar("T_Schema", bound="BaseModel")
Filter = tuple[str, Any] | tuple[str, str, Any] | Callable[[T_Model], ClauseElement]


class SortType(str, Enum):
    ASC = "asc"
    DESC = "desc"


def query_properties(*args: Any) -> Callable:
    def full_name_query(model: T_Model) -> ColumnElement[bool]:
        return func.concat(model.first_name, model.last_name).ilike(*args)

    return full_name_query


class BaseRepository(Generic[T_Model, T_Schema]):
    """
    Base CRUD Interface which maps Pydantic Schema onto SQLAlchemy database models
    """

    def __init__(
        self,
        model: Type[T_Model],
        schema: Type[T_Schema],
    ):
        self._model = model
        self._schema = schema

    async def create(self, session: AsyncSession, commit: bool = False, **kwargs: Any) -> T_Schema:
        """
        Add a new object
        """
        obj = self._model(**kwargs)
        session.add(obj)
        if commit:
            await session.commit()
        else:
            await session.flush()
        result = self._schema.model_validate(obj.to_dict())
        return result

    async def count(self, session: AsyncSession, filters: list[Filter] | None = None) -> int:
        query = sa.select(sa.func.count()).select_from(self._model)  # type: ignore
        if filters:
            query = query.where(sa.and_(*self._apply_filters(filters)))
        return (await session.execute(query)).scalar_one()

    async def _find_raw(
        self,
        session: AsyncSession,
        offset: int | None = None,
        limit: int | None = None,
        filters: list[Filter] | None = None,
        sort_options: list[tuple[str, SortType]] | None = None,
    ) -> Result:
        query = select(self._model)  # type: ignore
        if filters:
            query = query.where(and_(*self._apply_filters(filters)))

        if sort_options and len(sort_options) > 0:
            for field_name, sort_type in sort_options:
                query = query.order_by(
                    asc(field_name) if sort_type is SortType.ASC else desc(field_name)
                )

        query = query.offset(offset).limit(limit)
        return await session.execute(query)

    async def find_ids(
        self,
        session: AsyncSession,
        filters: list[Filter] | None = None,
    ) -> list[UUID]:
        query = sa.select([self._model.id])

        if filters:
            query = query.where(sa.and_(*self._apply_filters(filters)))

        result = await session.execute(query)
        return [row for row in result.scalars().all()]

    async def find(
        self,
        session: AsyncSession,
        offset: int | None = None,
        limit: int | None = None,
        filters: list[Filter] | None = None,
        sort_options: list[tuple[str, SortType]] | None = None,
    ) -> list[T_Schema]:
        """
        Find all results matching filters
        """
        result = await self._find_raw(
            session, offset=offset, limit=limit, filters=filters, sort_options=sort_options
        )
        return [self._schema.parse_obj(r.to_dict()) for r in result.scalars().all()]

    async def find_one(
        self,
        session: AsyncSession,
        filters: list[Filter] | None = None,
    ) -> T_Schema | None:
        """
        Find exactly one result matching filters
        """
        result = (await self._find_raw(session, filters=filters)).scalar_one_or_none()
        return self._schema.parse_obj(result.to_dict()) if result else None

    async def get_by_id(self, session: AsyncSession, id: UUID) -> T_Schema | None:
        """
        Get an object by id
        """
        return await self.find_one(session, filters=[("id", id)])

    async def update(
        self, session: AsyncSession, id: UUID, commit: bool = False, **kwargs: Any
    ) -> T_Schema:
        """
        Update object
        """
        query = sa.select(self._model).where(self._model.id == id)  # type: ignore
        obj = (await session.execute(query)).scalar_one()
        obj.from_dict(**kwargs)

        # The 'updated_at' field should be automatically updated to the current timestamp
        # each time an update operation is performed, irrespective of the specific fields
        # or relationships of the model that are being updated. This ensures that 'updated_at'
        # accurately reflects the most recent modification time for every instance of the model.
        obj.updated_at = sa.func.now()

        if commit:
            await session.commit()
        else:
            await session.flush()
        return self._schema.parse_obj(obj.to_dict())

    async def delete(self, session: AsyncSession, id: UUID, commit: bool = False) -> T_Schema:
        """
        Remove an object by id
        """
        query = sa.delete(self._model).where(self._model.id == id)  # type: ignore
        query = query.returning(self._model)  # type: ignore
        result = (await session.execute(query)).one()
        if commit:
            await session.commit()
        else:
            await session.flush()
        return self._schema(**{k: v for k, v in zip(result.keys(), result)})

    def _apply_filters(self, filter_list: list[Filter]) -> ClauseList:
        filters = ClauseList()
        for f in filter_list:
            if callable(f):
                filters.append(f(self._model))
            else:
                col = getattr(self._model, f[0])
                if len(f) > 2:
                    method = getattr(col, f[1])
                    filters.append(method(*f[2:]))
                else:
                    filters.append(col == f[1])
        return filters
