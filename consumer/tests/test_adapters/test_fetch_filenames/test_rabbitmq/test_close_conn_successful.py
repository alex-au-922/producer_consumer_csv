from src.adapters.fetch_filenames.rabbitmq import RabbitMQFetchFilenamesClient


def test_close_conn_successful(
    rabbitmq_fetch_filenames_no_wait_client: RabbitMQFetchFilenamesClient,
):
    for _ in rabbitmq_fetch_filenames_no_wait_client.fetch():
        pass
    assert rabbitmq_fetch_filenames_no_wait_client._conn is not None
    assert rabbitmq_fetch_filenames_no_wait_client.close()


def test_none_conn_close_successful(
    rabbitmq_fetch_filenames_client: RabbitMQFetchFilenamesClient,
):
    assert rabbitmq_fetch_filenames_client.close()
