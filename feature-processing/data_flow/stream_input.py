import json
from datetime import datetime
import time
from typing import Generic, Iterable, List, Optional, TypeVar

from config import settings
from utils.logging import get_logger

from mq import RabbitMQConnection
from bytewax.inputs import StatefulSourcePartition, FixedPartitionedSource

logger = get_logger(__name__)

DataT = TypeVar("DataT")  # all data from queue
MessageT = TypeVar("MessageT")  # all msgs from queue
# this are the queue datas and messages


class RabbitMQPartition(StatefulSourcePartition, Generic[DataT, MessageT]):
    """
    mq <--> bytewax
    statefulness -> save state of thw queue
    """

    def __init__(self, queue_name: str, resume_state: MessageT | None = None) -> None:
        self.queue_name = queue_name
        self._in_flight_msg_ids = resume_state or set()

        self.connection = RabbitMQConnection()
        self.connection.connect()

        self.channel = self.connection.get_channel()

    def next_batch(self, sched: Optional[datetime]) -> Iterable[DataT]:
        try:
            method_frame, header_frame, body = self.channel.basic_get(
                self.queue_name, auto_ack=True
            )
        except Exception:
            logger.error(
                f"error while fetching msg from queue", queue_name=self.queue_name
            )
            time.sleep(10)

            self.connection.connect()
            self.channel = self.connection.get_channel()
            return []

        if method_frame:
            msg_id = method_frame.delivery_tag
            self._in_flight_msg_ids.add(msg_id)
            return [json.loads(body)]

        else:
            return []

    def snapshot(self) -> MessageT:
        return self._in_flight_msg_ids

    def garbage_collect(self, state):
        closed_in_flight_msg_ids = state
        for msg_id in closed_in_flight_msg_ids:
            self.channel.basic_ack(delivery_tag=msg_id)
            self._in_flight_msg_ids.remove(msg_id)

    def close(self):
        self.channel.close()


class RabbitMQSource(FixedPartitionedSource):
    """
    fixed sources of data so fixed partitions
    """

    def list_parts(self) -> List[str]:
        return ["single_partition"]

    def build_part(
        self, now: datetime, for_part: str, resume_state: MessageT | None = None
    ) -> StatefulSourcePartition[DataT, MessageT]:
        return RabbitMQPartition(
            queue_name=settings.RABBITMQ_QUEUE_NAME,
        )
