import datetime
import re
import uuid
from typing import Any, Final, Literal, cast

from sqlalchemy import BigInteger, Column, MetaData, DateTime, String, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm.decl_api import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID

class RootBase(DeclarativeBase):
    metadata = MetaData()


ALREADY_SERIALIZED_T = Literal["<ALREADY_SERIALIZED>"]
ALREADY_SERIALIZED: Final = "<ALREADY_SERIALIZED>"


def camel_to_snake(name: str) -> str:
    # Taken from:
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case # noqa
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


# We are ignoring this because mypy cannot resolve dynamic base classes, and we want to use a proper
# base class rather than a class decorator for proper intellisense
# https://github.com/python/mypy/issues/5865
class Base(RootBase):  # type: ignore
    __abstract__ = True

    __name__: str

    # 'eager_defaults' is required for asyncio usage to ensure server-side assigned values
    # (ids, created_at, etc.) are loaded into the resultant session model after writing.
    # See https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#synopsis-orm for details.
    __mapper_args__ = {"eager_defaults": True}

    _table_name_override: str | None = None

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        if cls._table_name_override:
            return cls._table_name_override
        return camel_to_snake(cls.__name__)

    def __init__(self, **kwargs: Any) -> None:
        self.from_dict(**kwargs)

    def from_dict(self, **kwargs: Any) -> None:
        """
        Update a model with hierarchical data from a dictionary

        NOTE: This sets attributes within the model itself, but a flush/commit of the
        object needs to still be done to generate the appropriate queries.
        """

        readonly = self._readonly_fields if hasattr(self, "_readonly_fields") else []
        if hasattr(self, "_hidden_fields"):
            readonly += self._hidden_fields

        columns = self.__table__.columns
        relationships = self.__mapper__.relationships
        class_registry = self.registry._class_registry  # type: ignore
        properties = dir(self)

        # Update columns
        for key in columns.keys():
            if key.startswith("_"):
                continue
            if key not in readonly and key in kwargs:  # and getattr(self, key) != kwargs[key]:
                setattr(self, key, kwargs[key])

        # Update relationships
        for rel in relationships.keys():
            if rel.startswith("_"):
                continue
            if rel not in readonly and rel in kwargs:
                is_list = relationships[rel].uselist
                if is_list:
                    # List
                    # TODO
                    # This is somewhat complicated because we need to resolve the foreign key name
                    # used on the child object via the relationship. Then, check if it already
                    # exists in the object
                    continue
                else:
                    # Object
                    val = getattr(self, rel)

                    if val is None:
                        relationship_class = relationships[rel].argument

                        if isinstance(relationship_class, str):
                            # Sometimes we have to use string names in relationship() declaration
                            # to avoid circular imports. In that case, we need to resolve the class
                            relationship_class = class_registry[relationship_class]

                        val = relationship_class()
                        setattr(self, rel, val)
                    # from_dict won't stuck in the endless recursion because of this line
                    # we won't have source data for the backward child->parent relationship
                    # in the child's kwargs
                    if kwargs.get(rel, None) is not None:
                        val.from_dict(**kwargs[rel])
                    else:
                        setattr(self, rel, None)

        # Update any remaining properties that aren't columns or relationships
        for key in set(properties) - set(columns.keys()) - set(relationships.keys()):
            if (
                not key.startswith("_")
                and key not in readonly
                and key in kwargs
                and getattr(self.__class__, key).fset is not None
            ):
                setattr(self, key, kwargs[key])

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the model into a dictionary

        NOTE: This does not currently support models with list relationships.
        Should work for models with backrefs now
        """

        return cast(dict[str, Any], _serialize_recursively(model=self, trace=[]))


def _serialize_recursively(
    model: Base,
    trace: list[int],
) -> dict[str, Any] | ALREADY_SERIALIZED_T:
    columns = model.__table__.columns
    relationships = model.__mapper__.relationships
    properties = dir(model)
    result = {}

    if id(model) in trace:
        return ALREADY_SERIALIZED

    trace.append(id(model))

    # Get columns
    for key in columns.keys():
        if key.startswith("_"):
            continue
        result[key] = getattr(model, key)

    # Get relationships
    for key in relationships.keys():
        if key.startswith("_"):
            continue
        is_list = relationships[key].uselist
        if is_list:
            # Update a list
            # TODO
            # This is somewhat complicated because we need to resolve the foreign key name
            # used on the child object via the relationship. Then, check if it already
            # exists in the object
            continue
        else:
            # Associated object
            val = getattr(model, key)
            if val is not None:
                relationship_serialized = _serialize_recursively(model=val, trace=trace)
                if relationship_serialized is not ALREADY_SERIALIZED:
                    result[key] = relationship_serialized
            else:
                result[key] = None

    # Get any remaining properties that aren't columns or relationships
    for key in set(properties) - set(columns.keys()) - set(relationships.keys()):
        if not key.startswith("_"):
            result[key] = getattr(model, key)

    return result


class TopLevelModel(Base):
    """
    A top-level model is one managed by a repository and exposed at the API
    interface.
    """

    __abstract__ = True

    @declared_attr
    def id(self) -> Mapped[UUID]:
        return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    @declared_attr
    def created_at(self) -> Mapped[datetime.datetime]:
        return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    @declared_attr
    def updated_at(self) -> Mapped[datetime.datetime]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        )

    @declared_attr
    def deleted_at(self) -> Mapped[datetime.datetime]:
        return mapped_column(DateTime(timezone=True), nullable=True)

    @declared_attr
    def last_modified_by(self) -> Mapped[datetime.datetime]:
        return mapped_column(UUID(as_uuid=True), nullable=True)

    def to_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in self.__mapper__.column_attrs
        }
