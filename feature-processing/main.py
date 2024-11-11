import bytewax.operators as op
from bytewax.dataflow import Dataflow
from db import QdrantDBConnector

from data_flow.stream_input import RabbitMQSource
from data_flow.stream_output import QdrantOutput
from data_logic.dispatcher import (
    RawDispatcher,
    CleaningDispatcher,
    ChunkingDispatcher,
    EmbeddingDispatcher,
)

qdrant_connection = QdrantDBConnector()
flow = Dataflow("Streaming Ingestion Pipeline")
stream = op.input("input", RabbitMQSource())
stream = op.map("raw_dispatch", RawDispatcher.handle_mq_msg)
stream = op.map("cleaning_dispatch", CleaningDispatcher.dispatch_cleaner)
op.output(
    "cleaned data to qdrant",
    stream,
    QdrantOutput(connection=qdrant_connection, sink_type="clean"),
)

stream = op.flat_map("chunking_dispatch", ChunkingDispatcher.dispatch_chunker)
stream = op.map("embedding chunk dispatcher", EmbeddingDispatcher.dispatch_embedder)

op.output(
    "vector data to qdrant",
    stream,
    QdrantOutput(connection=qdrant_connection, sink_type="vector"),
)
