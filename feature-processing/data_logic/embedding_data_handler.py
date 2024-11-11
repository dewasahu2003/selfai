from abc import ABC, abstractmethod

from data_model.base import DataModel, VectorDBDataModel
from data_model.embedding_model import (
    ArticleEmbeddedChunkModel,
    PostEmbeddedChunkModel,
    RepoEmbeddedChunkModel,
)
from data_model.chunk_model import (
    ArticleChunkModel,
    PostChunkModel,
    RepoChunkModel,
)
from utils.embeddings import embedd_text, embedd_repositories


class EmbeddingDataHandler(ABC):
    """
    all data transformation for embedding will be done here
    """

    @abstractmethod
    def embedd(self, data_model: DataModel) -> VectorDBDataModel:
        pass


class PostEmbeddingHandler(EmbeddingDataHandler):
    """
    embedding data for post
    """

    def embedd(self, data_model: PostChunkModel) -> VectorDBDataModel:
        return PostEmbeddedChunkModel(
            entry_id=data_model.entry_id,
            type=data_model.type,
            platform=data_model.platform,
            author_id=data_model.author_id,
            chunk_content=data_model.chunk_content,
            chunk_id=data_model.chunk_id,
            embedded_content=embedd_text(data_model.chunk_content),
        )


class ArticleEmbeddingHandler(EmbeddingDataHandler):
    """
    embedding data for article
    """

    def embedd(self, data_model: ArticleChunkModel) -> VectorDBDataModel:
        return ArticleEmbeddedChunkModel(
            entry_id=data_model.entry_id,
            type=data_model.type,
            platform=data_model.platform,
            link=data_model.link,
            author_id=data_model.author_id,
            chunk_content=data_model.chunk_content,
            chunk_id=data_model.chunk_id,
            embedded_content=embedd_text(data_model.chunk_content),
        )


class RepoEmbeddingHandler(EmbeddingDataHandler):
    """
    embedding data for repo
    """

    def embedd(self, data_model: RepoChunkModel) -> VectorDBDataModel:
        return RepoEmbeddedChunkModel(
            entry_id=data_model.entry_id,
            type=data_model.type,
            name=data_model.name,
            link=data_model.link,
            owner_id=data_model.owner_id,
            chunk_content=data_model.chunk_content,
            chunk_id=data_model.chunk_id,
            embedded_content=embedd_repositories(data_model.chunk_content),
        )
