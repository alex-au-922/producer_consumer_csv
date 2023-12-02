from contextlib import contextmanager
from usecases import PublishFilenamesClient
import pika
from typing import Iterator, Optional, overload, Sequence, TYPE_CHECKING
from typing_extensions import override
from collections.abc import Callable
import logging

if TYPE_CHECKING:
    from pika.channel import Channel
    from pika.connection import Connection


class RabbitMQPublishFilenamesClient(PublishFilenamesClient):
    def __init__(
        self,
        host: str,
        port: int,
        credentials_service: Callable[[], tuple[str, str]],
        queue: str = "filenames",
    ) -> None:
        self._host = host
        self._port = port
        self._credentials_service = credentials_service
        self._queue = queue
        self._conn: Optional[Connection] = None

    @overload
    def publish(self, filename: str) -> bool:
        ...

    @overload
    def publish(self, filename: Sequence[str]) -> list[bool]:
        ...

    @override
    def publish(self, filename: str | Sequence[str]) -> bool | list[bool]:
        if isinstance(filename, str):
            return self._publish_single(filename)
        return self._publish_batch(filename)

    def _reset_conn(self) -> None:
        self._conn = None

    @contextmanager
    def _get_amqp_conn(self) -> Iterator[pika.BaseConnection]:
        if self._conn is None or self._conn.is_closed:
            username, password = self._credentials_service()
            credentials = pika.PlainCredentials(username, password)
            conn_parameters = pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                credentials=credentials,
            )
            self._conn = pika.BlockingConnection(conn_parameters)
        yield self._conn

    def _amqp_publish(self, channel: Channel, filename: str) -> None:
        channel.basic_publish(
            exchange="",
            routing_key=self._queue,
            body=filename,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )

    def _publish_single(self, filename: str) -> bool:
        try:
            with self._get_amqp_conn() as connection:
                channel = connection.channel()
                channel.queue_declare(
                    queue=self._queue,
                    durable=True,
                )
                channel.confirm_delivery()
                self._amqp_publish(channel, filename)
                return True
        except Exception as e:
            logging.exception(e)
            self._reset_conn()
            return False

    def _publish_batch(self, filenames: Sequence[str]) -> list[bool]:
        successes = []
        try:
            with self._get_amqp_conn() as connection:
                channel = connection.channel()
                channel.queue_declare(
                    queue=self._queue,
                    durable=True,
                )
                for filename in filenames:
                    try:
                        self._amqp_publish(channel, filename)
                        successes.append(True)
                    except Exception as e:
                        logging.exception(e)
                        successes.append(False)
        except Exception as e:
            logging.exception(e)
            self._reset_conn()
            return [False] * len(filenames)
        return successes

    @override
    def close(self) -> bool:
        try:
            if self._conn is not None:
                self._conn.close()
                return True
            return False
        except Exception as e:
            logging.exception(e)
            return False
