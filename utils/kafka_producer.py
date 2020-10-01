import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError

import settings

logger = logging.getLogger("persuasion_engine")


class Producer:
    producer = KafkaProducer(bootstrap_servers=settings.KAFKA_SERVER["host"])

    @staticmethod
    def on_success(args):
        message = "Pushed message to kafka successfully"
        logger.info(message)

    @staticmethod
    def on_failure(e):
        message = "Failed to push message to kafka " + repr(e)
        logger.error(message)

    @staticmethod
    def push_message(topic, key, value):
        """
        :param topic:
        :param key:
        :param value:
        :return: data
        """

        future = Producer.producer.send(topic, key=key, value=value). \
            add_callback(Producer.on_success).add_errback(Producer.on_failure)
        data = dict()
        try:
            result = future.get(timeout=60)
            data['topic'] = result.topic
            data['partition'] = result.partition
            data['offset'] = result.offset
        except KafkaError as e:
            Producer.on_failure(e)
        return data
