from src.adapters.fetch_filenames_stream.rabbitmq import (
    RabbitMQFetchFilenameStreamClient,
)


def test_close_conn_successful(
    rabbitmq_fetch_filenames_stream_no_wait_client: RabbitMQFetchFilenameStreamClient,
):
    for _ in rabbitmq_fetch_filenames_stream_no_wait_client.fetch_stream():
        pass
    assert rabbitmq_fetch_filenames_stream_no_wait_client._conn is not None
    assert rabbitmq_fetch_filenames_stream_no_wait_client.close()


def test_none_conn_close_successful(
    rabbitmq_fetch_filenames_stream_client: RabbitMQFetchFilenameStreamClient,
):
    assert rabbitmq_fetch_filenames_stream_client.close()
