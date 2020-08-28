import logging

from flask import jsonify

from databases.elasticsearch import ElasticSearch
from services.persuasion_builder import PersuasionBuilder
from services.persuasion_processor import PersuasionProcessor

logger = logging.getLogger("persuasion_engine")


class PersuasionServices:
    @staticmethod
    def create(request_data):
        try:
            meta = dict(push_to_es="true", push_to_inflow="true")
            response = PersuasionProcessor.process(request_data)
            PersuasionBuilder.publish_to_kafka(response, meta)
            return response
        except Exception as e:
            raise e

    @staticmethod
    def refresh(request_data, meta):
        try:
            p_id = request_data.get("p_id")
            logger.info("Getting updated data of persuasion - " + p_id)
            if not p_id:
                return jsonify(dict(status="failure", error="Please provide persuasion id"))
            es = ElasticSearch()
            existing_persuasion = es.get_persuasion(p_id)

            # Copying event_packet from existing persuasion
            request_data["data"] = existing_persuasion["meta"].get("event_packet")
            response = PersuasionProcessor.process(request_data)

            persuasion = PersuasionBuilder.update_persuasion(existing_persuasion, response)
            PersuasionBuilder.publish_to_kafka([persuasion], meta)
            return persuasion
        except Exception as e:
            raise e
