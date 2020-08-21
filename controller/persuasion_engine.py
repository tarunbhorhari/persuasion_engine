import json
import logging

from flask import Blueprint, jsonify, request

from databases.elasticsearch import ElasticSearch
from services.persuasion_builder import PersuasionBuilder
from services.persuasion_processor import PersuasionProcessor

persuasion_engine = Blueprint("persuasion_engine", __name__, template_folder="templates")
logger = logging.getLogger("persuasion_engine")


@persuasion_engine.route("/")
class PersuasionEngine:

    @staticmethod
    @persuasion_engine.route("/persuasion/create", methods=["POST"])
    def generate_persuasion():
        try:
            logger.info("Generating persuasion for an event")
            data = json.loads(request.data)
            meta = dict(push_to_es="true", push_to_inflow="true")
            response = PersuasionProcessor.process(data)
            PersuasionBuilder.publish_to_kafka(response, meta)
        except Exception as e:
            logger.error("Exception while creating persuasion " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))
        return jsonify(dict(status="success", data=response))

    @staticmethod
    @persuasion_engine.route("/persuasion/refresh", methods=["GET"])
    def get_persuasion():
        try:
            request_data = json.loads(request.data)
            p_id = request_data.get("p_id")
            logger.info("Getting updated data of persuasion - " + p_id)
            if not p_id:
                return jsonify(dict(status="failure", error="Please provide persuasion id"))
            es = ElasticSearch()
            persuasion = es.get_persuasion(p_id)
            if persuasion:
                request_data["data"] = persuasion["meta"].get("event_packet")
                response = PersuasionProcessor.process(request_data)
                # TODO - Persuasion Diff logic
                if response:
                    if response[0]["p_id"] == p_id:
                        response[0]["status"] = "UPDATED"
                    # TODO - Add expiry logic
                else:
                    response[0]["status"] = "RESOLVED"
                persuasion = response[0]
            PersuasionBuilder.publish_to_kafka(response, request.args)

        except Exception as e:
            error_msg = "Getting persuasion details - " + repr(e)
            logger.error(error_msg)
            return jsonify(dict(status="failure", error=error_msg))
        return jsonify(dict(status="success", data=persuasion if persuasion else dict()))
