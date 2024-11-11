from abc import ABC, abstractmethod

from data_model.base import DataModel
from data_model.clean_model import (
    ArticleCleanedModel,
    PostCleanedModel,
    RepoCleanedModel,
)
from data_model.raw import ArticleRawModel, PostRawModel, RepoRawModel
from utils.logging import get_logger

from utils.cleaning import clean_text


class CleaningDataHandler(ABC):
    """
    all data transformation for cleaning will be done here
    """

    @abstractmethod
    def clean(self, data_model: DataModel) -> DataModel:
        pass


class PostCleaningHandler(CleaningDataHandler):
    """
    cleaning data for post
    """

    def clean(self, data_model: PostRawModel) -> PostCleanedModel:
        return PostCleanedModel(
            entry_id=data_model.entry_id,
            platform=data_model.platform,
            author_id=data_model.author_id,
            cleaned_content=clean_text("".join(data_model.content.values())),
            image=data_model.image if data_model.image else None,
            type=data_model.type,
        )


class ArticleCleaningHandler(CleaningDataHandler):
    """
    cleaning data for article
    """

    def clean(self, data_model: ArticleRawModel) -> ArticleCleanedModel:
        return ArticleCleanedModel(
            entry_id=data_model.entry_id,
            type=data_model.type,
            platform=data_model.platform,
            link=data_model.link,
            cleaned_content=clean_text("".join(data_model.content.values())),
            author_id=data_model.author_id,
        )


class RepoCleaningHandler(CleaningDataHandler):
    """
    cleaning data for repo
    """

    def clean(self, data_model: RepoRawModel) -> RepoCleanedModel:
        return RepoCleanedModel(
            entry_id=data_model.entry_id,
            type=data_model.type,
            link=data_model.link,
            name=data_model.name,
            cleaned_content=clean_text("".join(data_model.content.values())),
            owner_id=data_model.owner_id,
        )
