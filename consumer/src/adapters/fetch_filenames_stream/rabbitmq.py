from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime
import time
from ...usecases import FetchFilenameStreamClient
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from pika.connection import Connection
from typing import Generator, Iterator, Optional, Sequence, cast, overload
from typing_extensions import override
from collections.abc import Callable
import logging


class RabbitMQFetchFilenameStreamClient(FetchFilenameStreamClient[int]):
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
        self._channel: Optional[BlockingChannel] = None
        self._polling_timeout = polling_timeout
        self._last_poll_time: Optional[datetime] = None

    @overload
    def ack(self, message_receipt: int) -> bool:
        ...

    @overload
    def ack(self, message_receipt: Sequence[int]) -> list[bool]:
        ...

    @override
    def ack(self, message_receipt: int | Sequence[int]) -> bool | list[bool]:
        if isinstance(message_receipt, int):
            return self._ack_single(message_receipt)
        return self._ack_batch(message_receipt)

    def _ack_single(self, message_receipt: int) -> bool:
        try:
            with self._get_channel() as channel:
                channel.basic_ack(delivery_tag=message_receipt, multiple=False)
            return True
        except Exception as e:
            logging.exception(e)
            return False

    def _ack_batch(self, message_receipts: Sequence[int]) -> list[bool]:
        #! RabbitMQ is not thread-safe, so we have to use a single thread to ack
        results: list[bool] = []
        for receipt in message_receipts:
            results.append(self._ack_single(receipt))
        return results

    @overload
    def reject(self, message_receipt: int) -> bool:
        ...

    @overload
    def reject(self, message_receipt: Sequence[int]) -> list[bool]:
        ...

    @override
    def reject(self, message_receipt: int | Sequence[int]) -> bool | list[bool]:
        if isinstance(message_receipt, int):
            return self._reject_single(message_receipt)
        return self._reject_batch(message_receipt)

    def _reject_single(self, message_receipt: int) -> bool:
        try:
            with self._get_channel() as channel:
                channel.basic_nack(delivery_tag=message_receipt, requeue=True)
            return True
        except Exception as e:
            logging.exception(e)
            return False

    def _reject_batch(self, message_receipts: Sequence[int]) -> list[bool]:
        #! RabbitMQ is not thread-safe, so we have to use a single thread to ack
        results: list[bool] = []
        for receipt in message_receipts:
            results.append(self._reject_single(receipt))
        return results

    def _reset_conn(self) -> None:
        self._conn = None
        self._channel = None

    @contextmanager
    def _get_amqp_conn(self) -> Iterator[Connection]:
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

    @contextmanager
    def _get_channel(self) -> Iterator[BlockingChannel]:
        if self._channel is None or self._channel.is_closed:
            with self._get_amqp_conn() as connection:
                self._channel = connection.channel()
        yield self._channel

    def _wait(self) -> None:
        time.sleep(0.5)

    @override
    def fetch_stream(self) -> Generator[tuple[str, int], None, None]:
        while True:
            try:
                method: Optional[Basic.Deliver] = None
                with self._get_channel() as channel:
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

                    yield body.decode(), cast(int, method.delivery_tag)

            except Exception as e:
                logging.exception(e)
                if method is not None:
                    self.reject(method.delivery_tag)
                self._reset_conn()

    @override
    def close(self) -> bool:
        try:
            if self._channel is not None:
                self._channel.close()
            if self._conn is not None:
                self._conn.close()
            return True
        except Exception as e:
            logging.exception(e)
            return False
