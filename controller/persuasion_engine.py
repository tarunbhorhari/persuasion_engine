import json

from flask import Blueprint, jsonify, request

from services.persuasion_processor import PersuasionProcessor

persuasion_engine = Blueprint('persuasion_engine', __name__, template_folder='templates')


@persuasion_engine.route("/")
class PersuasionEngine:

    @staticmethod
    @persuasion_engine.route("/persuasion/create", methods=["POST"])
    def generate_persuasion():
        data = json.loads(request.data)
        response = PersuasionProcessor.process(data)
        return jsonify(response)
