import concurrent.futures
import json
import logging

from flask import Blueprint, jsonify, request

from services.persuasion_services import PersuasionServices
from settings.constants import MAX_WORKERS

persuasion_engine = Blueprint("persuasion_engine", __name__, template_folder="templates")
logger = logging.getLogger("persuasion_engine")


@persuasion_engine.route("/")
class PersuasionEngine:

    @staticmethod
    @persuasion_engine.route("/persuasion/create", methods=["POST"])
    def create_persuasion():
        try:
            logger.info("Generating persuasion for an event")
            request_data = json.loads(request.data)
            # TODO - TARUN - Add loop over persuasion_type and run for all the sub_type
            response = PersuasionServices.create(request_data)
        except Exception as e:
            logger.error("Exception while creating persuasion " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))
        return jsonify(dict(status="success", data=response))

    @staticmethod
    @persuasion_engine.route("/persuasion/refresh", methods=["GET"])
    def refresh_persuasion():
        try:
            request_data = json.loads(request.data)
            meta = request.args
            persuasion = PersuasionServices.refresh(request_data, meta)
        except Exception as e:
            error_msg = "Getting persuasion details - " + repr(e)
            logger.error(error_msg)
            return jsonify(dict(status="failure", error=error_msg))
        return jsonify(dict(status="success", data=persuasion if persuasion else dict()))

    @staticmethod
    @persuasion_engine.route("/persuasion/bulk/create", methods=["POST"])
    def bulk_create():
        logger.info("Creating persuasions in bulk")
        try:
            request_data = json.loads(request.data)
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                {executor.submit(PersuasionServices.create, data): data for data in request_data}

            return jsonify(
                dict(status="success", message="Your request is in the queue, persuasion will create shortly"))
        except Exception as e:
            logger.error("Exception while creating persuasions in bulk - " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))

    @staticmethod
    @persuasion_engine.route("/persuasion/bulk/refresh", methods=["GET"])
    def bulk_refresh():
        logger.info("Refreshing/Updating persuasions in bulk")
        try:
            request_data = json.loads(request.data)
            meta = request.args
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                {executor.submit(PersuasionServices.refresh, data, meta): data for data in request_data}

            return jsonify(
                dict(status="success", message="Your request is in the queue, persuasion will be updated shortly"))
        except Exception as e:
            logger.error("Exception while creating persuasions in bulk - " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))
