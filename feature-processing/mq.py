import pika
import pika.exceptions

from utils.logging import get_logger
from config import settings

logger = get_logger(__name__)


class RabbitMQConnection:
    _instance = None

    def __new__(
        cls,
        host: str = None,
        port: int = None,
        username: str | None = None,
        password: str | None = None,
        virtual_host: str = "/",
    ):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        virtual_host: str = "/",
        fail_silently: bool = False,
        **kwargs,
    ):
        self.host = host or settings.RABBITMQ_HOST
        self.port = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_DEFAULT_USERNAME
        self.password = password or settings.RABBITMQ_DEFAULT_PASSWORD
        self.virtual_host = virtual_host
        self.fail_silently = fail_silently
        self._connection = None

    def connect(self):
        try:
            _credentials = pika.PlainCredentials(
                username=self.username, password=self.password
            )
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=_credentials,
                )
            )
        except pika.exceptions.AMQPConnectionError as e:
            logger.exception(f"failed to connect to rabbitmq: {e}")
            if not self.fail_silently:
                raise e

    def is_connected(self):
        return self._connection if not None else self._connection.is_open

    def get_channel(self):
        if self.is_connected():
            return self._connection.channel()

    def close(self):
        if self.is_connected():
            self._connection.close()
            self._connection = None
            logger.info("rabbitmq connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self):
        self.close()

    def publish_message(self, data: str, queue: str):
        # get channel
        channel = self.get_channel()
        # declare queue
        channel.queue_declare(
            queue=queue, durable=True, exclusive=False, auto_delete=False
        )
        # confirm that queue can deliver
        channel.confirm_delivery()
        try:
            # publish message
            channel.basic_publish(
                exchange="",
                routing_key=queue,
                body=data,
                mandatory=True,
            )
            logger.info(
                "sent message to rabbitmq", queue_type="rabbitMQ", queue_name=queue
            )
        except pika.exceptions.UnroutableError:
            logger.info(
                "failed to send message to rabbitmq",
                queue_type="rabbitMQ",
                queue_name=queue,
            )
