import json
import logging

from flask import Blueprint, jsonify, request

from services.persuasion_processor import PersuasionProcessor
from settings.app_constants import KAFKA_SERVER
from utils.kafka_producer import Producer

persuasion_engine = Blueprint('persuasion_engine', __name__, template_folder='templates')
logger = logging.getLogger("persuasion_engine")


@persuasion_engine.route("/")
class PersuasionEngine:

    @staticmethod
    @persuasion_engine.route("/persuasion/create", methods=["POST"])
    def generate_persuasion():
        try:
            logger.info("Generating persuasion for an event")
            data = json.loads(request.data)
            response = PersuasionProcessor.process(data)
            # Publishing each persuasion to kafka
            for persuasion in response:
                kafka_response = PersuasionEngine.publish_to_kafka(persuasion)
                logger.info(kafka_response)
        except Exception as e:
            logger.error("Exception while creating persuasion " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))
        return jsonify(dict(status="success", data=response))

    @staticmethod
    @persuasion_engine.route("/persuasion/", methods=["GET"])
    def get_persuasion():
        try:
            data = json.loads(request.data)
            if not data.get("p_id"):
                return jsonify(dict(status="failure", error="Please provide persuasion id"))
            response = PersuasionProcessor.process(data)
        except Exception as e:
            error_msg = "Excepting while getting persuasion details - " + repr(e)
            logger.error(error_msg)
            return jsonify(dict(status="failure", error=error_msg))
        return jsonify(dict(status="success", data=response[0] if response else dict()))

    @classmethod
    def publish_to_kafka(cls, persuasion):
        kafka_resp = dict()
        try:
            topic = KAFKA_SERVER["TOPIC"]["PERSUASION"]
            producer = Producer()
            key = persuasion["p_id"].encode("utf-8")
            value = json.dumps(persuasion).encode("utf-8")
            kafka_resp = producer.push_message(topic, key, value)
        except Exception as e:
            logger.critical("Exception while pushing persuasion to kafka - " + repr(e))
        return kafka_resp
