from ...adapters.fetch_filenames_stream.rabbitmq import (
    RabbitMQFetchFilenameStreamClient,
)
from ...adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from ...adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
from .config import RabbitMQConfig, PostgresConfig, CSVParserConfig
from .setup_logging import setup_logging
from ...entities import IOTRecord
import logging

setup_logging()

logging.getLogger("pika").setLevel(logging.ERROR)


def _upsert_iot_records_buffer(
    iot_records_buffer: list[IOTRecord],
    upsert_iot_records_client: PostgresUpsertIOTRecordsClient,
) -> None:
    successes = upsert_iot_records_client.upsert(iot_records_buffer)

    if not all(successes):
        raise Exception("Failed to upsert all records!")


def main() -> None:
    fetch_filenames_stream_client = RabbitMQFetchFilenameStreamClient(
        host=RabbitMQConfig.HOST,
        port=RabbitMQConfig.PORT,
        credentials_service=lambda: (RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD),
        queue=RabbitMQConfig.QUEUE,
        polling_timeout=RabbitMQConfig.POLLING_TIMEOUT,
    )

    file_parse_iot_records_client = CSVParseIOTRecordsClient(
        recognized_datetime_formats=CSVParserConfig.RECOGNIZED_DATETIME_FORMATS,
        delimiter=CSVParserConfig.DELIMITER,
        file_extension=CSVParserConfig.FILE_EXTENSION,
    )

    upsert_iot_records_client = PostgresUpsertIOTRecordsClient(
        host=PostgresConfig.HOST,
        port=PostgresConfig.PORT,
        credentials_service=lambda: (PostgresConfig.USERNAME, PostgresConfig.PASSWORD),
        database=PostgresConfig.DATABASE,
        batch_upsert_size=PostgresConfig.BATCH_UPSERT_SIZE,
    )

    try:
        for filename, receipt in fetch_filenames_stream_client.fetch_stream():
            logging.info(f"Upserting {filename}...")
            iot_records_buffer: list[IOTRecord] = []
            try:
                for iot_record in file_parse_iot_records_client.parse_stream(filename):
                    iot_records_buffer.append(iot_record)

                    if len(iot_records_buffer) < PostgresConfig.BATCH_UPSERT_SIZE:
                        continue

                    _upsert_iot_records_buffer(
                        iot_records_buffer, upsert_iot_records_client
                    )
                    iot_records_buffer.clear()

                if len(iot_records_buffer) > 0:
                    _upsert_iot_records_buffer(
                        iot_records_buffer, upsert_iot_records_client
                    )

                logging.info(f"Successfully upserted {filename}!")
                fetch_filenames_stream_client.ack(receipt)
            except Exception as e:
                logging.exception(e)
                fetch_filenames_stream_client.reject(receipt)
                logging.error(f"Failed to upsert {filename}!")
            finally:
                iot_records_buffer.clear()
    except Exception as e:
        logging.exception(e)
        raise e
    finally:
        fetch_filenames_stream_client.close()
        upsert_iot_records_client.close()


if __name__ == "__main__":
    main()
