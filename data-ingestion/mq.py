import pika
import pika.exceptions
from config import settings


class RabbitMQConnection:
    """
    singeton class for connecting with rabbitmq
    """

    _instance = None

    def __new__(
        cls,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        virtual_host: str = "/",
    ):
        if cls._instance is None:
            cls._instance = super().__new__(
                cls,
            )
        return cls._instance

    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
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

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        try:
            _credentials = pika.PlainCredentials(
                username=self.username, password=self.password
            )
            self._connection = pika.BlockingConnection(
                parameters=pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=_credentials,
                    # heartbeat=600,
                    # blocked_connection_timeout=300,
                )
            )
        except pika.exceptions.AMQPConnectionError as e:
            print(f"failed to connect to rabbitmq: {e}")
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
            print("rabbitmq connection closed")


def publish_to_mq(queue_name: str, data: str):
    """
    method for pusing data into queue
    """
    try:
        mq_conn = RabbitMQConnection()
        with mq_conn:
            # get channnel
            channel = mq_conn.get_channel()
            # ensure queue exists
            channel.queue_declare(queue=queue_name, durable=True)
            # confirm that queue can deliver
            channel.confirm_delivery()
            # publish data
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=data,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent msg
                    # content_type="application/json",
                ),
            )
            print(f"data published to {queue_name}")
    except pika.exceptions.UnroutableError:
        print("data not routed to queue")
    except Exception as e:
        print(f"failed to publish data: {e}")
