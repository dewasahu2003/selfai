from typing import Optional
from base import DataModel


class PostChunkModel(DataModel):
    entry_id: str
    type: str

    platform: str
    author_id: str
    chunk_content: str
    image: Optional[str] = None

    chunk_id: str


class ArticleChunkModel(DataModel):
    entry_id: str
    type: str

    platform: str
    link: str
    chunk_content: str
    author_id: str

    chunk_id: str


class RepoChunkModel(DataModel):
    entry_id: str
    type: str

    name: str
    link: str
    chunk_content: str
    owner_id: str

    chunk_id: str
