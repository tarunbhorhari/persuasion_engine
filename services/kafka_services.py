import json
import logging

from settings.constants import KAFKA_SERVER
from utils.kafka_producer import Producer

logger = logging.getLogger("persuasion_engine")


class KafkaServices:

    @classmethod
    def publish_to_watson_kafka(cls, persuasion):
        kafka_resp = dict()
        try:
            topic = KAFKA_SERVER["TOPIC"]["WATSON"]
            producer = Producer()
            key = persuasion["p_id"].encode("utf-8")
            value = json.dumps(persuasion).encode("utf-8")
            kafka_resp = producer.push_message(topic, key, value)
        except Exception as e:
            logger.critical("Exception while pushing persuasion to kafka - " + repr(e))
        return kafka_resp

    @classmethod
    def publish_to_inflow_kafka(cls, persuasion):
        kafka_resp = dict()
        try:
            topic = KAFKA_SERVER["TOPIC"]["INFLOW"]
            producer = Producer()
            key = persuasion["p_id"].encode("utf-8")
            value = json.dumps(persuasion).encode("utf-8")
            kafka_resp = producer.push_message(topic, key, value)
        except Exception as e:
            logger.critical("Exception while pushing persuasion to kafka - " + repr(e))
        return kafka_resp

    @staticmethod
    def publish_to_kafka(response, args):
        """
        Common function to publish persuasions on multiple kafka
        :param response:
        :param args:
        :return:
        """
        for persuasion in response:
            if args.get("push_to_es", "false") == "true":
                watson_kafka_response = KafkaServices.publish_to_watson_kafka(persuasion)
                logger.info(watson_kafka_response)
            if args.get("push_to_inflow", "false") == "true":
                inflow_kafka_response = KafkaServices.publish_to_inflow_kafka(persuasion)
                logger.info(inflow_kafka_response)
