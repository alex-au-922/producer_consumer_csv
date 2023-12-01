import pathlib
from typing import Iterator
from adapters.upsert_filenames.rabbitmq import RabbitMQUpsertFilenamesClient
from .config import RabbitMQConfig, ProjectConfig
from .setup_logging import setup_logging
import logging

setup_logging()

upsert_filenames_client = RabbitMQUpsertFilenamesClient(
    host=RabbitMQConfig.HOST,
    port=RabbitMQConfig.PORT,
    username=RabbitMQConfig.USERNAME,
    password=RabbitMQConfig.PASSWORD,
    queue=RabbitMQConfig.QUEUE,
)

def traverse_files() -> Iterator[str]:
    for filename in pathlib.Path(ProjectConfig.TARGET_FILE_DIR).glob(f'*{ProjectConfig.TARGET_FILE_EXTENSION}'):
        yield filename

def main() -> None:
    try:
       successes_map = upsert_filenames_client.upsert_stream(traverse_files())
       failed_filenames = [filename for filename, success in successes_map.items() if not success]
       if failed_filenames:
           raise Exception(f'Failed to upsert filenames: {failed_filenames}')
    except Exception as e:
        logging.exception(e)
        raise e
    finally:
        upsert_filenames_client.close()

if __name__ == '__main__':
    main()
        