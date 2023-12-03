import os


class LoggingConfig:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    LOG_DATE_FORMAT = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
    LOG_DIR = os.getenv("LOG_DIR", "/tmp")
    LOG_RETENTION = os.getenv("LOG_RETENTION", "7")
    LOG_ROTATION = os.getenv("LOG_ROTATION", "midnight")


class RabbitMQConfig:
    HOST = os.getenv("RABBITMQ_HOST", "localhost")
    PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    USERNAME = os.getenv("RABBITMQ_USERNAME", "guest")
    PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    QUEUE = os.getenv("RABBITMQ_QUEUE_NAME", "filenames")
    POLLING_TIMEOUT = int(os.getenv("RABBITMQ_POLLING_TIMEOUT", 10))


class PostgresConfig:
    HOST = os.getenv("POSTGRES_HOST", "localhost")
    PORT = int(os.getenv("POSTGRES_PORT", 5432))
    USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
    PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")
    BATCH_UPSERT_SIZE = int(os.getenv("POSTGRES_BATCH_UPSERT_SIZE", 1000))


class CSVParserConfig:
    RECOGNIZED_DATETIME_FORMATS = os.getenv(
        "CSV_PARSER_RECOGNIZED_DATETIME_FORMATS", ""
    ).split(",")
    DELIMITER = os.getenv("CSV_PARSER_DELIMITER", ",")
    FILE_EXTENSION = os.getenv("CSV_PARSER_FILE_EXTENSION", ".csv")
