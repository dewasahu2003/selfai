from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, UUID4, ConfigDict
from errors import ImproperlyConfigured
import uuid
import pymongo
from typing import List, Optional
from pymongo import errors
from utils import get_logger
from db.mongo import connections

_database = connections.get_database("data-crawling")
logger = get_logger(__name__)


class BaseDocument(BaseModel):
    """
    base class for all documents
    """

    id: UUID4 = Field(default_factory=uuid.uuid4)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict):
        "for convering _id:str to id:uuid"
        if not data:
            return data
        id = data.get("_id")
        return cls(**dict(data, id=id))

    def to_mongo(self, **kwargs):
        "for convering id:uuid to _id:str"
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)
        parsed = self.model_dump(
            by_alias=by_alias, exclude_unset=exclude_unset, **kwargs
        )
        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))
        return parsed

    def save(
        self,
        **kwargs,
    ):
        _collection = _database[self._get_collection_name()]
        try:
            result = _collection.insert_one(self.to_mongo(**kwargs))
            return result.inserted_id
        except errors.WriteError:
            logger.exception("Error saving document")
            return None

    @classmethod
    def bulk_insert(cls, documents: List, **kwargs) -> Optional[List[str]]:
        _collection = _database[cls._get_collection_name()]
        try:
            result = _collection.insert_many(
                [doc.to_mongo(**kwargs) for doc in documents]
            )
            return result.inserted_ids
        except errors.WriteError:
            logger.exception("Error saving multiple document")
            return None

    @classmethod
    def get_or_create(cls, **kwargs) -> Optional[str]:
        _collection = _database[cls._get_collection_name()]
        try:
            instance = _collection.find_one(kwargs)
            if instance:
                return str(cls.from_mongo(instance).id)
            new_instance = cls(**kwargs)
            new_instance = new_instance.save()
            return new_instance
        except errors.OperationFailure:
            logger.exception("Error getting or creating document")
            return None

    @classmethod
    def _get_collection_name(cls):
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ImproperlyConfigured(
                "doc not defined with setting config with name of collection"
            )
        return cls.Settings.name
