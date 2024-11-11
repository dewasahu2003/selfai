from typing import List
from bytewax.outputs import StatelessSinkPartition, DynamicSink
from qdrant_client.http.api_client import UnexpectedResponse
from qdrant_client.models import Batch

from db import QdrantDBConnector
from data_model.base import VectorDBDataModel

from utils.logging import get_logger

logger = get_logger(__name__)


class QdrantOutput(DynamicSink):
    """
    bytewax <--> qdrant
    dynamic -> for concurrent workers working -> for diff sink destination -> vector and non-vector
    """

    def __init__(self, connection: QdrantDBConnector, sink_type: str):
        self._connection = connection
        self._sink_type = sink_type

        try:
            collection_name = "cleaned_posts"
            self._connection.get_collection(collection_name=collection_name)
        except UnexpectedResponse:
            logger.info(
                "could not access collection,creating one ...",
                collection_name=collection_name,
            )
            self._connection.create_non_vector_collection(
                collection_name=collection_name
            )

        try:
            collection_name = "cleaned_articles"
            self._connection.get_collection(collection_name=collection_name)
        except UnexpectedResponse as e:
            logger.info(
                "could not access collection,creating one ...",
                collection_name=collection_name,
            )
            self._connection.create_non_vector_collection(
                collection_name=collection_name
            )

        try:
            collection_name = "cleaned_repositories"
            self._connection.get_collection(collection_name=collection_name)
        except UnexpectedResponse:
            logger.info(
                "could not access collection,creating one ...",
                collection_name=collection_name,
            )
            self._connection.create_non_vector_collection(
                collection_name=collection_name
            )

        try:
            vector_collection_name = "vector_posts"
            self._connection.get_collection(collection_name=vector_collection_name)
        except UnexpectedResponse:
            logger.info(
                "could not access collection,creating one ...",
                collection_name=vector_collection_name,
            )
            self._connection.create_vector_collection(
                collection_name=vector_collection_name
            )

        try:
            vector_collection_name = "vector_articles"
            self._connection.get_collection(collection_name=vector_collection_name)
        except UnexpectedResponse:
            logger.info(
                "could not access collection,creating one ...",
                collection_name=vector_collection_name,
            )
            self._connection.create_vector_collection(
                collection_name=vector_collection_name
            )

        try:
            vector_collection_name = "vector_repositories"
            self._connection.get_collection(collection_name=vector_collection_name)
        except UnexpectedResponse:
            logger.info(
                "could not access collection,creating one ...",
                collection_name=vector_collection_name,
            )
            self._connection.create_vector_collection(
                collection_name=vector_collection_name
            )

    def build(self, worket_index: int, worker_count: int) -> StatelessSinkPartition:
        if self._sink_type == "clean":
            return QdrantCleanedDataSink(
                connection=self._connection,
            )
        elif self._sink_type == "vector":
            return QdrantVectorDataSink(
                connection=self._connection,
            )
        else:
            raise ValueError(f"invalid sink type: {self._sink_type}")


class QdrantCleanedDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDBConnector):
        self._connection = connection

    def write_batch(self, items: List[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, data = zip(*payloads)
        # here there are chances of error
        collection_name = get_clean_collection(data_type=data[0]["type"])
        self._connection.write_data(
            collection_name=collection_name,
            points=Batch(ids=ids, vectors={}, payloads=data),
        )
        logger.info(
            "data written to qdrant for clean data points",
            collection_name=collection_name,
            num=len(ids),
        )


class QdrantVectorDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDBConnector):
        self._connection = connection

    def write_batch(self, items: List[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, vectors, meta_data = zip(*payloads)
        # here possiblity of error
        collection_name = get_vector_collection(data_type=meta_data[0]["type"])
        self._connection.write_data(
            collection_name=collection_name,
            points=Batch(ids=ids, vectors=vectors, payloads=meta_data),
        )
        logger.info("data written to qdrant for vector datapoints", num=len(ids))


def get_clean_collection(data_type: str):
    if data_type == "posts":
        return "cleaned_posts"
    elif data_type == "articles":
        return "cleaned_articles"
    elif data_type == "repositories":
        return "cleaned_repositories"
    else:
        raise ValueError(f"invalid data type: {data_type}")


def get_vector_collection(data_type: str) -> str:
    if data_type == "posts":
        return "vector_posts"
    elif data_type == "articles":
        return "vector_articles"
    elif data_type == "repositories":
        return "vector_repositories"
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
