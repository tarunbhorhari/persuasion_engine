import json
import logging

from flask import Blueprint, jsonify, request

from services.persuasion_processor import PersuasionProcessor

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
        except Exception as e:
            logger.error("Exception while creating persuasion " + repr(e))
            return jsonify(dict())
        return jsonify(response)
