import pathlib
from typing import Iterator
from ...adapters.publish_filenames.rabbitmq import RabbitMQPublishFilenamesClient
from .config import RabbitMQConfig, ProjectConfig
from .setup_logging import setup_logging
import logging

setup_logging()

logging.getLogger("pika").setLevel(logging.WARNING)


def traverse_files() -> Iterator[str]:
    for filename in pathlib.Path(ProjectConfig.TARGET_FILE_DIR).glob(
        f"*{ProjectConfig.TARGET_FILE_EXTENSION}"
    ):
        yield str(filename)


def main() -> None:
    publish_filenames_client = RabbitMQPublishFilenamesClient(
        host=RabbitMQConfig.HOST,
        port=RabbitMQConfig.PORT,
        credentials_service=lambda: (RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD),
        queue=RabbitMQConfig.QUEUE,
    )

    successes_map = {}
    try:
        logging.info("Publishing filenames...")

        for filename in traverse_files():
            logging.info(f"Publishing {filename}...")
            successes_map[filename] = publish_filenames_client.publish(filename)

        failed_filenames = [
            filename for filename, success in successes_map.items() if not success
        ]
        if failed_filenames:
            raise Exception(f"Failed to publish filenames: {failed_filenames}")
        logging.info("Successfully published all filenames")
    except Exception as e:
        logging.exception(e)
        raise e
    finally:
        logging.info("Closing publish filenames client...")
        publish_filenames_client.close()


if __name__ == "__main__":
    main()
