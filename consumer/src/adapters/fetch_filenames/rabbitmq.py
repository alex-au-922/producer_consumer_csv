from contextlib import contextmanager
from datetime import datetime
import time
from ...usecases import FetchFilenameClient
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from pika.connection import Connection
from typing import Generator, Iterator, Optional
from typing_extensions import override
from collections.abc import Callable
import logging


class RabbitMQFetchFilenamesClient(FetchFilenameClient):
    def __init__(
        self,
        host: str,
        port: int,
        credentials_service: Callable[[], tuple[str, str]],
        queue: str = "filenames",
        polling_timeout: int = 10,
    ) -> None:
        self._host = host
        self._port = port
        self._credentials_service = credentials_service
        self._queue = queue
        self._conn: Optional[Connection] = None
        self._polling_timeout = polling_timeout
        self._last_poll_time: Optional[datetime] = None

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

    def _wait(self) -> None:
        time.sleep(0.5)

    @override
    def fetch(self) -> Generator[str, None, None]:
        while True:
            try:
                method: Optional[Basic.Deliver] = None
                with self._get_amqp_conn() as connection:
                    channel: BlockingChannel = connection.channel()
                    channel.queue_declare(queue=self._queue, durable=True)
                    properties: Optional[BasicProperties]
                    body: Optional[bytes]

                    method, properties, body = channel.basic_get(
                        queue=self._queue, auto_ack=False
                    )
                    if method is None and properties is None and body is None:
                        if self._last_poll_time is None:
                            self._last_poll_time = datetime.now()
                        if (
                            datetime.now() - self._last_poll_time
                        ).total_seconds() > self._polling_timeout:
                            break
                        self._wait()
                        continue

                    self._last_poll_time = None

                    yield body.decode()

                    channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.exception(e)
                if method is not None:
                    channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
                self._reset_conn()

    @override
    def close(self) -> bool:
        try:
            if self._conn is not None:
                self._conn.close()
            return True
        except Exception as e:
            logging.exception(e)
            return False
