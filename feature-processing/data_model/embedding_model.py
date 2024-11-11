from typing import Optional, Tuple
from base import VectorDBDataModel

import numpy as np


class PostEmbeddedChunkModel(VectorDBDataModel):
    entry_id: str
    type: str

    platform: str
    author_id: str
    chunk_content: str
    embedded_content: np.ndarray

    chunk_id: str

    class Config:
        arbitrary_types_allowed = True

    def to_payload(self) -> Tuple[str, np.ndarray, dict]:
        data = {
            "id": self.entry_id,
            "platform": self.platform,
            "content": self.chunk_content,
            "owner_id": self.author_id,
            "type": self.type,
        }
        return self.chunk_id, self.embedded_content, data


class ArticleEmbeddedChunkModel(VectorDBDataModel):
    entry_id: str
    type: str

    platform: str
    link: str
    chunk_content: str
    embedded_content: np.ndarray
    author_id: str

    chunk_id: str

    class Config:
        arbitrary_types_allowed = True

    def to_payload(self) -> Tuple[str, np.ndarray, dict]:
        data = {
            "id": self.entry_id,
            "platform": self.platform,
            "content": self.chunk_content,
            "owner_id": self.author_id,
            "author_id": self.author_id,
            "type": self.type,
        }
        return self.chunk_id, self.embedded_content, data


class RepoEmbeddedChunkModel(VectorDBDataModel):
    entry_id: str
    type: str

    name: str
    link: str
    chunk_content: str
    embedded_content: np.ndarray
    owner_id: str

    chunk_id: str

    class Config:
        arbitrary_types_allowed = True

    def to_payload(self) -> Tuple[str, np.ndarray, dict]:
        data = {
            "id": self.entry_id,
            "name": self.name,
            "content": self.chunk_content,
            "link": self.link,
            "owner_id": self.owner_id,
            "type": self.type,
        }
        return self.chunk_id, self.embedded_content, data
