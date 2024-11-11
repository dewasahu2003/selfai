from abc import ABC, abstractmethod
from pydantic import BaseModel


class DataModel(BaseModel):
    """
    abstract class for all datatype
    """

    entry_id: str
    type: str


class VectorDBDataModel(ABC, DataModel):
    """
    abstract class for all datatype that needs to be stored in vectordb
    """

    entry_id: str
    type: str

    @abstractmethod
    def to_payload(self) -> tuple:
        pass
