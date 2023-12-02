from contextlib import contextmanager
from ...usecases import FetchFilenameClient
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from pika.connection import Connection
from typing import Iterator, Optional
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

    @override
    def fetch(self) -> Iterator[str]:
        while True:
            try:
                with self._get_amqp_conn() as connection:
                    channel: BlockingChannel = connection.channel()
                    channel.queue_declare(queue=self._queue, durable=True)

                    method: Optional[Basic.Deliver]
                    properties: Optional[BasicProperties]
                    body: Optional[bytes]
                    for method, properties, body in channel.consume(
                        queue=self._queue, inactivity_timeout=self._polling_timeout
                    ):
                        if method == None and properties == None and body == None:
                            raise StopIteration
                        try:
                            yield body.decode("utf-8")
                            channel.basic_ack(delivery_tag=method.delivery_tag)
                        except Exception as e:
                            logging.exception(e)
                            channel.basic_nack(delivery_tag=method.delivery_tag)
                            raise e
            except StopIteration:
                logging.info("No more filenames to fetch")
                break
            except Exception as e:
                logging.exception(e)
                self._reset_conn()
                raise e

    @override
    def close(self) -> bool:
        try:
            if self._conn is not None:
                self._conn.close()
            return True
        except Exception as e:
            logging.exception(e)
            return False
