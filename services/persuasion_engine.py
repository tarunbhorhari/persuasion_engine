import json
import logging
import uuid
from datetime import timedelta

import settings
from databases.elasticsearch import ElasticSearch
from databases.mysql import MYSQL
from services.config_keeper import ConfigKeeperAPI
from utils.utils import *

# from itertools import groupby
# from operator import itemgetter

logger = logging.getLogger("persuasion_engine")


class PersuasionEngine:
    TEMPLATES = ConfigKeeperAPI.get_config(settings.CONFIG_KEEPER_SERVICE_NAME, settings.CONFIG_KEEPER_CATEGORY)

    @staticmethod
    def process(request_data):
        """
        Common function to create all type of persuasion
        :param request_data: Event packet
        :return: Persuasion Object
        """

        # This code is to read template from local
        # base_path = "/Users/tarun.bhorhari/projects/persuasion_engine/projects/templates/"
        # file_path = "%s%s_%s.json" % (base_path, request_data.get("type"), request_data.get("sub_type"))
        # TODO - Add request data validations if any

        sub_type = request_data.get("sub_type")
        persuasion_type = request_data.get("type")
        # Fetching persuasion configs here
        templates = [PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type))] if sub_type else [
            PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type)) for sub_type in
            settings.TEMPLATE_CHOICES[persuasion_type] if
            PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type))]

        persuasion_resp = []
        logger.info("Processing persuasion config")

        # with open(file_path) as persuasion_template:
        #     template = json.load(persuasion_template)
        for template in templates:
            persuasion_template = copy.deepcopy(template)
            source_data = persuasion_template.get("source", {})
            Utils.evaluate_data(source_data.get("params", dict()), request_data.get("data"))

            try:
                persuasion_resp = PersuasionEngine.build_persuasion(request_data, source_data, persuasion_template)
            except Exception as e:
                logger.error("Exception while processing persuasion config - " + repr(e))
                raise e

        return persuasion_resp

    @staticmethod
    def build_persuasion(body, source_data, template):
        """

        :param body: Event packet
        :param query_resp: Source response
        :param template: Persuasion config
        :return: A persuasion
        """

        persuasions = []
        source_resp = PersuasionEngine.get_source_response(source_data, body)
        if not source_resp:
            return persuasions

        try:
            response = dict()
            response["event_source"] = body.get("source", "")
            response["latest_event_source"] = body.get("source", "")
            response["event_created_on"] = body.get("created_on", "")
            response["meta"] = body.get("meta", {})
            response["meta"].update(dict(event_packet=body.get("data", {})))

            # Initializing query response to key mapping
            resp = Utils.template_source_keys_mapping(source_resp, template["source"]["keys_mapping"])

            # Grouping logic
            # group = template.get("source", {}).get("group_by")
            # grouper = itemgetter(*group)

            # for k, v in groupby(data, grouper):
            #     response["data"] = list(v)
            for data in resp:
                response["data"] = data
                # This will update the static data
                response["data"].update(template["source"]["static_keys_mapping"])
                response["p_id"] = Utils.format_data(template["p_id"], response["data"])

                # Adding workflow details
                response["workflow"] = copy.deepcopy(template["workflow"])
                response["workflow"]["consumers"] = Utils.render_template_for_consumers(data, response["workflow"].get(
                    "consumers", {}))

                persuasion = PersuasionEngine.create_persuasion_object(response, template)
                persuasions.append(persuasion)

        except Exception as e:
            logger.error("Exception while building persuasions" + repr(e))
            raise e

        return persuasions

    @classmethod
    def create_persuasion_object(cls, response, template):
        """

        :param response: Raw persuasion
        :param template: Config
        :return: Final persuasion object
        """
        persuasion_obj = dict(response)
        try:
            today = datetime.datetime.now()
            persuasion_obj["UUID"] = str(uuid.uuid1())
            persuasion_obj["title"] = template["title"]
            persuasion_obj["type"] = template["type"]
            persuasion_obj["sub_type"] = template["sub_type"]
            persuasion_obj["tags"] = template["tags"]
            persuasion_obj["status"] = settings.PERSUASION_STATUS[0]
            persuasion_obj["created_on"] = str(today.strftime(settings.DATE_TIME_FORMAT))
            persuasion_obj["modified_on"] = str(today.strftime(settings.DATE_TIME_FORMAT))
            expiry_date = timedelta(days=template["expiry_days"]) + today
            persuasion_obj["expiry_date"] = str(expiry_date.strftime(settings.DATE_TIME_FORMAT))

        except Exception as e:
            logger.error("Exception is creating persuasion object - " + repr(e))
            raise e
        return persuasion_obj

    @staticmethod
    def update_persuasion(old_persuasion, response):
        """
        Generalized logic to refresh persuasion
        :param old_persuasion: Existing persuasion
        :param response: New persuasions list
        :return: Updated persuasion
        """

        new_persuasion = next((p for p in response if p["p_id"] == old_persuasion["p_id"]), None)
        today = datetime.datetime.now()
        # Case 1st if persuasion doesn't exist
        if not new_persuasion:
            old_persuasion["modified_on"] = str(today.strftime(settings.DATE_TIME_FORMAT))
            old_persuasion["latest_event_source"] = new_persuasion["latest_event_source"]
            old_persuasion["status"] = settings.PERSUASION_STATUS[3]
            return old_persuasion

        # Case 2nd If it's expired
        expiry_date = datetime.datetime.strptime(old_persuasion["expiry_date"], settings.DATE_TIME_FORMAT)

        new_persuasion["expiry_date"] = old_persuasion["expiry_date"]
        new_persuasion["created_on"] = old_persuasion["created_on"]
        new_persuasion["event_source"] = old_persuasion["event_source"]

        if today > expiry_date:
            new_persuasion["status"] = settings.PERSUASION_STATUS[2]
        else:
            # Case 3rd If it's updated
            new_persuasion["status"] = settings.PERSUASION_STATUS[1]
        return new_persuasion

    @staticmethod
    def get_source_response(source_data, request_data):
        """
        This function will evaluate the source and send the row in list

        :param source_data: Config source packet
        :param request_data: Event packet
        :return: Source response
        """
        response = None
        logger.info("Fetching data source response")
        ds_name = source_data.get('ds_name')
        if ds_name == "mysql":
            query = Utils.format_data(source_data.get("execute", ""), source_data.get("params", dict()))
            response = json.loads(MYSQL.fetch_data(query))

        elif ds_name == "es":
            query = Utils.evaluate_data(source_data.get("execute", ""), source_data.get("params", dict()))
            es = ElasticSearch(settings.STATIC_DATA_ELASTIC_SEARCH["host"],
                               settings.STATIC_DATA_ELASTIC_SEARCH["protocol"],
                               settings.STATIC_DATA_ELASTIC_SEARCH["port"])
            response = es.get_response(source_data.get("index", ""), query)

        elif ds_name == "lambda":
            package = source_data.get("package", "").replace("/", ".")
            name = source_data.get("execute", "")
            execute = getattr(__import__(package, fromlist=[name]), name)
            response = execute(request_data, source_data.get("params"))

        return response
