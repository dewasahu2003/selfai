import hashlib
from abc import ABC, abstractmethod

from data_model.base import DataModel
from data_model.chunk_model import (
    ArticleChunkModel,
    PostChunkModel,
    RepoChunkModel,
)
from data_model.clean_model import (
    ArticleCleanedModel,
    PostCleanedModel,
    RepoCleanedModel,
)

from utils.chunking import chunk_text


class ChunkingDataHandler(ABC):
    """
    all data transformation for chunking will be done here
    """

    @abstractmethod
    def chunk(self, data_model: DataModel) -> list[DataModel]:
        pass


class PostChunkingHandler(ChunkingDataHandler):
    """
    chunking data for post
    """

    def chunk(self, data_model: PostCleanedModel) -> list[DataModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(
            text_content,
        )

        for chunk in chunks:
            model = PostChunkModel(
                entry_id=data_model.entry_id,
                type=data_model.type,
                platform=data_model.platform,
                author_id=data_model.author_id,
                chunk_content=chunk,
                image=data_model.image if data_model.image else None,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
            )
            data_models_list.append(model)
        return data_models_list


class ArticleChunkingHandler(ChunkingDataHandler):
    """
    chunking data for article
    """

    def chunk(self, data_model: ArticleCleanedModel) -> list[DataModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(
            text_content,
        )
        for chunk in chunks:
            model = ArticleChunkModel(
                entry_id=data_model.entry_id,
                type=data_model.type,
                platform=data_model.platform,
                link=data_model.link,
                author_id=data_model.author_id,
                chunk_content=chunk,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
            )
            data_models_list.append(model)
        return data_models_list


class RepoChunkingHandler(ChunkingDataHandler):
    """
    chunking data for repo
    """

    def chunk(self, data_model: RepoCleanedModel) -> list[DataModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(
            text_content,
        )
        for chunk in chunks:
            model = RepoChunkModel(
                entry_id=data_model.entry_id,
                type=data_model.type,
                name=data_model.name,
                link=data_model.link,
                owner_id=data_model.owner_id,
                chunk_content=chunk,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
            )
            data_models_list.append(model)
        return data_models_list
