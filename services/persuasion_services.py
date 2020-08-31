import logging

from flask import jsonify

from databases.elasticsearch import ElasticSearch
from services.kafka_services import KafkaServices
from services.persuasion_engine import PersuasionEngine

logger = logging.getLogger("persuasion_engine")


class PersuasionServices:
    @staticmethod
    def create(request_data):
        try:
            meta = dict(push_to_es="true", push_to_inflow="true")
            response = PersuasionEngine.process(request_data)
            KafkaServices.publish_to_kafka(response, meta)
            return response
        except Exception as e:
            raise e

    @staticmethod
    def refresh(request_data, args):
        try:
            p_id = request_data.get("p_id")
            logger.info("Getting updated data of persuasion - " + p_id)
            if not p_id:
                return jsonify(dict(status="failure", error="Please provide persuasion id"))
            es = ElasticSearch()
            existing_persuasion = es.get_persuasion(p_id)
            request_data["type"] = existing_persuasion.get("type")
            request_data["sub_type"] = existing_persuasion.get("sub_type")

            # Copying event_packet from existing persuasion
            request_data["data"] = existing_persuasion["meta"].get("event_packet")
            response = PersuasionEngine.process(request_data)

            persuasion = PersuasionEngine.update_persuasion(existing_persuasion, response)
            KafkaServices.publish_to_kafka([persuasion], args)
            return persuasion
        except Exception as e:
            raise e
