from contextlib import contextmanager
from usecases import UpsertFilenamesClient
import pika
from pika.channel import Channel
from pika.connection import Connection
from typing import Iterator, Optional, override, overload
import logging

class RabbitMQUpsertFilenamesClient(UpsertFilenamesClient):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        queue: str = 'filenames',
    ) -> None:
        credentials = pika.PlainCredentials(username, password)
        self._conn_parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials,
        )
        self._queue = queue
        self._conn: Optional[Connection] = None
    
    @overload
    def upsert(self, filename: str) -> bool:
        ...
    
    @overload
    def upsert(self, filename: list[str]) -> bool:
        ...
    
    @override
    def upsert(self, filename: str | list[str]) -> bool | list[bool]:
        if isinstance(filename, str):
            return self._upsert_single(filename)
        return self._upsert_batch(filename)

    @override
    def upsert_stream(self, filename_iterator: Iterator[str]) -> dict[str, bool]:
        successes_map: dict[str, bool] = {}
        try:
            for filename in filename_iterator:
                success = self._upsert_single(filename)
                successes_map[filename] = success
        except Exception as e:
            logging.exception(e)
        return successes_map

    @contextmanager
    def _get_amqp_conn(self) -> Iterator[pika.BaseConnection]:
        if self._conn is None or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._conn_parameters)
        yield self._conn
    
    def _publish_one(self, channel: Channel, filename: str) -> None:
        channel.basic_publish(
            exchange='',
            routing_key=self._queue,
            body=filename,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            ),
        )

    def _upsert_single(self, filename: str) -> bool:
        try:
            with self._get_amqp_conn() as connection:
                channel = connection.channel()
                channel.queue_declare(
                    queue=self._queue,
                    durable=True,
                )
                channel.confirm_delivery()
                self._publish_one(channel, filename)
                return True
        except Exception as e:
            logging.exception(e)
            return False
    
    def _upsert_batch(self, filenames: list[str]) -> list[bool]:
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
                        self._publish_one(channel, filename)
                        successes.append(True)
                    except Exception as e:
                        logging.exception(e)
                        successes.append(False)
        except Exception as e:
            logging.exception(e)
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
        