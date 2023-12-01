import os

class ProjectConfig:
    TARGET_FILE_DIR = os.getenv('TARGET_FILE_DIR', '/tmp')
    TARGET_FILE_EXTENSION = os.getenv('TARGET_FILE_EXTENSION', '.csv')

class LoggingConfig:
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_DATE_FORMAT = os.getenv('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
    LOG_DIR = os.getenv('LOG_DIR', '/tmp')
    LOG_RETENTION = os.getenv('LOG_RETENTION', '7')
    LOG_ROTATION = os.getenv('LOG_ROTATION', 'midnight')
    
class RabbitMQConfig:
    HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    USERNAME = os.getenv('RABBITMQ_USERNAME', 'guest')
    PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    QUEUE = os.getenv('RABBITMQ_QUEUE', 'filenames')
    