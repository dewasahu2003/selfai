from utils.logging import get_logger

from cleaning_data_handler import (
    ArticleCleaningHandler,
    CleaningDataHandler,
    PostCleaningHandler,
    RepoCleaningHandler,
)
from chunking_data_handler import (
    ArticleChunkingHandler,
    ChunkingDataHandler,
    PostChunkingHandler,
    RepoChunkingHandler,
)
from embedding_data_handler import (
    ArticleEmbeddingHandler,
    EmbeddingDataHandler,
    PostEmbeddingHandler,
    RepoEmbeddingHandler,
)

from data_model.base import DataModel
from data_model.raw import ArticleRawModel, PostRawModel, RepoRawModel

logger = get_logger(__name__)


class RawDispatcher:
    @staticmethod
    def handle_mq_msg(msg: dict) -> DataModel:
        data_type = msg["type"]
        logger.info("received msg: ", data_type=data_type)

        if data_type == "posts":
            return PostRawModel(**msg)
        elif data_type == "articles":
            return ArticleRawModel(**msg)
        elif data_type == "repositories":
            return RepoRawModel(**msg)
        else:
            raise ValueError(f"Invalid data type: {data_type}")


class CleaningHandlerFactory:
    @staticmethod
    def create_handler(data_type: str) -> CleaningDataHandler:
        if data_type == "posts":
            return PostCleaningHandler()
        elif data_type == "articles":
            return ArticleCleaningHandler()
        elif data_type == "repositories":
            return RepoCleaningHandler()
        else:
            raise ValueError(f"Invalid data type: {data_type}")


class CleaningDispatcher:
    cleaning_factory = CleaningHandlerFactory

    @classmethod
    def dispatch_cleaner(cls, data_model: DataModel) -> DataModel:
        data_type = (data_model.type,)
        handler = cls.cleaning_factory.create_handler(data_type)
        clean_model = handler.clean(data_model)

        logger.info(
            "data cleaned succesfully ",
            data_type=data_type,
            cleaned_model_len=len(clean_model.cleaned_content),
        )
        return clean_model


class ChunkingHandlerFactory:
    @staticmethod
    def create_handler(data_type: str) -> ChunkingDataHandler:
        if data_type == "posts":
            return PostChunkingHandler()
        elif data_type == "articles":
            return ArticleChunkingHandler()
        elif data_type == "repositories":
            return RepoChunkingHandler()
        else:
            raise ValueError(f"Invalid data type: {data_type}")


class ChunkingDispatcher:
    chunking_factory = ChunkingHandlerFactory

    @classmethod
    def dispatch_chunker(cls, data_model: DataModel) -> DataModel:
        data_type = (data_model.type,)
        handler = cls.chunking_factory.create_handler(data_type)
        chunked_model = handler.chunk(data_model)
        logger.info(
            "data chunked succesfully ",
            data_type=data_type,
            chunked_model_len=len(chunked_model),
        )
        return chunked_model


class EmbeddingHandlerFactory:
    @staticmethod
    def create_handler(data_type: str) -> EmbeddingDataHandler:
        if data_type == "posts":
            return PostEmbeddingHandler()
        elif data_type == "articles":
            return ArticleEmbeddingHandler()
        elif data_type == "repositories":
            return RepoEmbeddingHandler()
        else:
            raise ValueError(f"Invalid data type: {data_type}")


class EmbeddingDispatcher:
    embedding_factory = EmbeddingHandlerFactory

    @classmethod
    def dispatch_embedder(cls, data_model: DataModel) -> DataModel:
        data_type = data_model.type
        handler = cls.embedding_factory.create_handler(data_type)
        embedding_model = handler.embedd(data_model)
        logger.info(
            "data embedded succesfully ",
            data_type=data_type,
            embedding_model_len=len(embedding_model),
        )
        return embedding_model
