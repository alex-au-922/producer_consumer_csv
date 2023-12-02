from ...adapters.fetch_filenames.rabbitmq import RabbitMQFetchFilenamesClient
from ...adapters.file_parse_iot_records.csv import CSVParseIOTRecordsClient
from ...adapters.upsert_iot_records.postgres import PostgresUpsertIOTRecordsClient
from .config import RabbitMQConfig, PostgresConfig, CSVParserConfig
from setup_logging import setup_logging
import logging
from ...entities import IOTRecord

setup_logging()

fetch_filenames_client = RabbitMQFetchFilenamesClient(
    host=RabbitMQConfig.HOST,
    port=RabbitMQConfig.PORT,
    username=RabbitMQConfig.USERNAME,
    password=RabbitMQConfig.PASSWORD,
    queue=RabbitMQConfig.QUEUE,
    polling_timeout=RabbitMQConfig.POLLING_TIMEOUT,
)

file_parse_iot_records_client = CSVParseIOTRecordsClient(
    recognized_datetime_formats=CSVParserConfig.RECOGNIZED_DATETIME_FORMATS,
    delimiter=CSVParserConfig.DELIMITER,
)

upsert_iot_records_client = PostgresUpsertIOTRecordsClient(
    host=PostgresConfig.HOST,
    port=PostgresConfig.PORT,
    username=PostgresConfig.USERNAME,
    password=PostgresConfig.PASSWORD,
    database=PostgresConfig.DATABASE,
    batch_upsert_size=PostgresConfig.BATCH_UPSERT_SIZE,
)


def main() -> None:
    filestream_buffer: list[IOTRecord] = []
    try:
        for filename in fetch_filenames_client.fetch():
            for iot_record in file_parse_iot_records_client.parse_stream(filename):
                filestream_buffer.append(iot_record)
                if len(filestream_buffer) >= PostgresConfig.BATCH_UPSERT_SIZE:
                    upsert_iot_records_client.upsert(filestream_buffer)
                    filestream_buffer.clear()
        if filestream_buffer:
            upsert_iot_records_client.upsert(filestream_buffer)
            filestream_buffer.clear()
    except Exception as e:
        logging.exception(e)
        raise e
    finally:
        fetch_filenames_client.close()
        upsert_iot_records_client.close()


if __name__ == "__main__":
    main()
