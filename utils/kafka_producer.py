import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError

from settings.app_constants import KAFKA_SERVER

logger = logging.getLogger("persuasion_engine")


class Producer:
    producer = None

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER["HOST"])

    def on_success(self):
        message = "Pushed message to kafka successfully"
        logger.info(message)

    def on_failure(self, e):
        message = "Failed to push message to kafka " + repr(e)
        logger.error(message)

    def push_message(self, topic, key, value):

        future = self.producer.send(topic, key=key, value=value).add_callback(self.on_success).add_errback(
            self.on_failure)
        data = dict()
        try:
            result = future.get(timeout=60)
            data['topic'] = result.topic
            data['partition'] = result.partition
            data['offset'] = result.offset
        except KafkaError as e:
            self.on_failure(e)
        return data
