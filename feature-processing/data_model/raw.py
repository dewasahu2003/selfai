from typing import Optional
from base import DataModel


class RepoRawModel(DataModel):
    name: str
    link: str
    content: dict
    owner_id: str


class PostRawModel(DataModel):
    platform: str
    content: dict
    author_id: str | None = None
    image: Optional[str] = None


class ArticleRawModel(DataModel):
    name: str
    platform: str
    link: str
    content: dict
    author_id: str
