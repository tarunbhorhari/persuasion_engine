import concurrent.futures
import json
import logging

from flask import Blueprint, jsonify, request

import settings
from services.persuasion_services import PersuasionServices

persuasion_engine = Blueprint("persuasion_engine", __name__, template_folder="templates")
logger = logging.getLogger("persuasion_engine")


@persuasion_engine.route("/")
class PersuasionEngineBluePrint:

    @staticmethod
    @persuasion_engine.route("/", methods=["GET"])
    def send_response():
        return jsonify("Hi Ironic, you have landed successfully here !!!")

    @staticmethod
    @persuasion_engine.route("/persuasion/create", methods=["POST"])
    def create_persuasion():
        """
        API - /persuasion/create
        {
            "type": "inventory",
            "sub_type": "sold_out",
            "p_id": null,
            "source": "watson",
            "created_on": "2020-07-10 07:30:45",
            "data": {
                "hotel_id": 149,
                "date": "2017-04-01",
                "is_room_active": 1
            },
            "meta": {}
        }
        :return: persuasion object
        """
        try:
            logger.info("Generating persuasion for an event")
            request_data = json.loads(request.data)
            response = PersuasionServices.create(request_data)
        except Exception as e:
            logger.error("Exception while creating persuasion " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))
        return jsonify(dict(status="success", data=response))

    @staticmethod
    @persuasion_engine.route("/persuasion/bulk/create", methods=["POST"])
    def bulk_create():
        """
        This will create persuasions in bulk and will push it to ES
        API - /persuasion/bulk/create
        [
            {
                "type": "inventory",
                "sub_type": "sold_out",
                "p_id": null,
                "source": "watson",
                "created_on": "2020-08-07 00:00:00",
                "data": {
                    "hotel_id": 149,
                    "date": "2017-04-01",
                    "is_room_active": 1
                },
                "meta": {}
            }
        ]
        :return: success/failure message
        """
        logger.info("Creating persuasions in bulk")
        try:
            request_data = json.loads(request.data)
            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
                {executor.submit(PersuasionServices.create, data): data for data in request_data}

            return jsonify(
                dict(status="success", message="Your request is in the queue, persuasion will create shortly"))
        except Exception as e:
            logger.error("Exception while creating persuasions in bulk - " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))

    @staticmethod
    @persuasion_engine.route("/persuasion/refresh", methods=["GET"])
    def refresh_persuasion():
        """
        This will update the persuasion and will return it
        API - /persuasion/refresh?push_to_es=true&push_to_inflow=false
        {
            "type": "inventory",
            "sub_type": "sold_out",
            "p_id": "quality_score_inventory_depth_45000405199_2020-09-01",
            "source": "watson",
            "created_on": "2020-07-10 07:30:45",
            "data": {},
            "meta": {}
        }
        :push_to_es - This will push updated persuasion to Watson ES
        :push_to_inflow - This will push updated persuasion to Workflow
        :return:
        """
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
    @persuasion_engine.route("/persuasion/bulk/refresh", methods=["GET"])
    def bulk_refresh():
        """
        This will update persuasions in bulk and will push it to ES
        API - /persuasion/bulk/refresh?push_to_es=true&push_to_inflow=false
        [
            {
                "type": "inventory",
                "sub_type": "sold_out",
                "p_id": "quality_score_inventory_depth_45000405199_2020-09-01",
                "source": "watson",
                "created_on": "2020-07-10 07:30:45",
                "data": {},
                "meta": {}
            }
        ]
        :push_to_es - This will push updated persuasion to Watson ES
        :push_to_inflow - This will push updated persuasion to Workflow
        :return: success/failure message
        """
        logger.info("Refreshing/Updating persuasions in bulk")
        try:
            request_data = json.loads(request.data)
            args = request.args
            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
                {executor.submit(PersuasionServices.refresh, data, args): data for data in request_data}

            return jsonify(
                dict(status="success", message="Your request is in the queue, persuasion will be updated shortly"))
        except Exception as e:
            logger.error("Exception while creating persuasions in bulk - " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))

    @staticmethod
    @persuasion_engine.route("/persuasion/schedule/refresh", methods=["GET"])
    def schedule_refresh():
        """
        This will also update persuasions in bulk based on type subtype and will push it to ES
        API - /persuasion/schedule/refresh?push_to_es=true&push_to_inflow=false&type=quality_score&sub_type=inventory_depth

        :push_to_es - This will push updated persuasion to Watson ES
        :push_to_inflow - This will push updated persuasion to Workflow
        :return: success/failure message
        """
        logger.info("Refreshing/Updating persuasions in bulk")
        try:
            args = request.args
            if not args.get("type") or not args.get("sub_type"):
                return jsonify(
                    dict(status="failure", message="Invalid type/sub_type"))

            persuasions_request = PersuasionServices.get_persuasions_request_from_es(args)

            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
                {executor.submit(PersuasionServices.refresh, data, args): data for data in persuasions_request}

            return jsonify(
                dict(status="success", message="Your request is in the queue, persuasion will be updated shortly"))
        except Exception as e:
            logger.error("Exception while creating persuasions in bulk - " + repr(e))
            return jsonify(dict(status="failure", error=repr(e)))
