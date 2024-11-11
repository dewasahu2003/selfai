from pydantic import Field
from .base import BaseDocument


class UserDoc(BaseDocument):
    first_name: str
    last_name: str

    class Settings:
        name = "users"


class RepositoryDoc(BaseDocument):
    name: str
    link: str
    content: dict
    owner_id: str = Field(alias="owner_id")

    class Settings:
        name = "repositories"


class ArticleDoc(BaseDocument):
    platform: str
    link: str
    content: dict
    author_id: str = Field(alias="author_id")

    class Settings:
        name = "articles"


class PostDoc(BaseDocument):
    platform: str
    content: dict
    author_id = Field(alias="author_id")

    class Settings:
        name = "posts"
