from contextlib import contextmanager
import logging
from typing import Iterator, Optional, Sequence, overload, TYPE_CHECKING, final, TypeVar
from typing_extensions import override
import psycopg2
from usecases import UpsertIOTRecordsClient
from entities import IOTRecord
from collections.abc import Callable

if TYPE_CHECKING:
    from psycopg2.extensions import connection

T = TypeVar("T")


@final
class PostgresUpsertIOTRecordsClient(UpsertIOTRecordsClient):
    def __init__(
        self,
        host: str,
        port: int,
        credentials_service: Callable[[], tuple[str, str]],
        database: str,
        batch_upsert_size: int = 1000,
    ) -> None:
        self._host = host
        self._port = port
        self._credentials_service = credentials_service
        self._database = database
        self._batch_upsert_size = batch_upsert_size
        self._conn: Optional[connection] = None

    @overload
    def upsert(self, iot_record: IOTRecord) -> bool:
        ...

    @overload
    def upsert(self, iot_record: Sequence[IOTRecord]) -> list[bool]:
        ...

    @override
    def upsert(self, iot_record: IOTRecord | Sequence[IOTRecord]) -> bool | list[bool]:
        if isinstance(iot_record, IOTRecord):
            return self._upsert_single(iot_record)
        return self._upsert_batch(iot_record)

    def _reset_conn(self) -> None:
        self._conn = None

    @contextmanager
    def _get_conn(self) -> Iterator[connection]:
        if self._conn is None or self._conn.closed:
            username, password = self._credentials_service()
            self._conn = psycopg2.connect(
                host=self._host,
                port=self._port,
                user=username,
                password=password,
                database=self._database,
            )
        yield self._conn

    def _get_sql_stmt(self) -> str:
        stmt = """
            INSERT INTO records(
                record_time,
                sensor_id,
                value
            ) VALUES (
                %(datetime)s,
                %(sensor_id)s,
                %(value)s
            ) ON CONFLICT (record_time, sensor_id) DO UPDATE SET
                value = EXCLUDED.value
        """
        return stmt

    def _transform_iot_record_to_sql_dict(
        self,
        iot_record: IOTRecord,
    ) -> dict:
        return {
            "record_time": iot_record.record_time,
            "sensor_id": iot_record.sensor_id,
            "value": iot_record.value,
        }

    def _batch_generator(
        self,
        iterable: Sequence[T],
        batch_size: int,
    ) -> Iterator[Sequence[T]]:
        for i in range(0, len(iterable), batch_size):
            yield iterable[i : i + batch_size]

    def _upsert_single(self, iot_record: IOTRecord) -> bool:
        try:
            with self._get_conn() as conn, conn.cursor() as cursor:
                try:
                    cursor.execute(
                        self._get_sql_stmt(),
                        self._transform_iot_record_to_sql_dict(iot_record),
                    )
                    conn.commit()
                    return True
                except Exception as e:
                    conn.rollback()
                    logging.exception(e)
                    return False
        except Exception as e:
            logging.exception(e)
            self._reset_conn()
            return False

    def _upsert_batch(self, iot_records: Sequence[IOTRecord]) -> list[bool]:
        successes: list[bool] = []
        for batch in self._batch_generator(iot_records, self._batch_upsert_size):
            try:
                with self._get_conn() as conn, conn.cursor() as cursor:
                    try:
                        cursor.executemany(
                            self._get_sql_stmt(),
                            [
                                self._transform_iot_record_to_sql_dict(iot_record)
                                for iot_record in batch
                            ],
                        )
                        conn.commit()
                        successes.extend([True] * len(batch))
                    except Exception as e:
                        conn.rollback()
                        logging.exception(e)
                        successes.extend([False] * len(batch))
            except Exception as e:
                logging.exception(e)
                self._reset_conn()
                successes.extend([False] * len(batch))
        return successes
