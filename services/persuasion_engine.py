import json
import json
import logging
import uuid
from datetime import timedelta

from databases.elasticsearch import ElasticSearch
from databases.mysql import MYSQL
from services.config_keeper import ConfigKeeperAPI
from settings.constants import PERSUASION_STATUS, DATE_FORMAT, CONFIG_KEEPER_SERVICE_NAME, CONFIG_KEEPER_CATEGORY, \
    STATIC_DATA_ELASTIC_SEARCH
from utils.utils import *

# from itertools import groupby
# from operator import itemgetter

logger = logging.getLogger("persuasion_engine")


class PersuasionEngine:
    TEMPLATES = ConfigKeeperAPI.get_config(CONFIG_KEEPER_SERVICE_NAME, CONFIG_KEEPER_CATEGORY)

    @staticmethod
    def process(request_data):
        base_path = "/Users/tarun.bhorhari/projects/persuasion_engine/templates/"
        file_path = "%s%s_%s.json" % (base_path, request_data.get("type"), request_data.get("sub_type"))
        # TODO - Add request data validations if any

        # sub_type = request_data.get("sub_type")
        # persuasion_type = request_data.get("type")
        # templates = [PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type))] if sub_type else [
        #     PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type)) for sub_type in
        #     TEMPLATE_CHOICES[persuasion_type] if PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type))]

        persuasion_resp = []
        logger.info("Processing persuasion config")
        with open(file_path) as persuasion_template:
            # for template in templates:
            template = json.load(persuasion_template)
            source_data = template.get("source", {})
            Utils.evaluate_data(source_data.get("params", dict()), request_data.get("data"))

            try:
                source_resp = PersuasionEngine.get_source_response(source_data)
                persuasion_resp = PersuasionEngine.build_persuasion(request_data, source_resp,
                                                                    template) if source_resp else list()
            except Exception as e:
                logger.error("Exception while processing persuasion config - " + repr(e))
                raise e

        return persuasion_resp

    @staticmethod
    def build_persuasion(body, query_resp, template):
        persuasions = []
        try:
            response = dict()
            response["event_source"] = body.get("source", "")
            response["latest_event_source"] = body.get("source", "")
            response["event_created_on"] = body.get("created_on", "")
            response["meta"] = body.get("meta", {})
            response["meta"].update(dict(event_packet=body.get("data", {})))

            # Initializing query response to key mapping
            resp = Utils.template_source_keys_mapping(query_resp, template["source"]["keys_mapping"])
            # response["consumers"] = Utils.render_template_for_wf_consumers(resp, template["workflow"]["consumers"])

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
                response["consumers"] = Utils.render_template_for_wf_consumers(data, template["workflow"]["consumers"])
                persuasion = PersuasionEngine.create_persuasion_object(response, template)
                persuasions.append(persuasion)

        except Exception as e:
            logger.error("Exception while building persuasions" + repr(e))
            raise e

        return persuasions

    @classmethod
    def create_persuasion_object(cls, response, template):
        persuasion_obj = dict(response)
        try:
            persuasion_obj["UUID"] = str(uuid.uuid1())
            persuasion_obj["title"] = template["title"]
            persuasion_obj["type"] = template["type"]
            persuasion_obj["sub_type"] = template["sub_type"]
            persuasion_obj["tags"] = template["tags"]
            persuasion_obj["status"] = PERSUASION_STATUS[0]
            persuasion_obj["created_on"] = str(datetime.datetime.now())
            persuasion_obj["modified_on"] = str(datetime.datetime.now())
            persuasion_obj["expiry_date"] = str(timedelta(days=template["expiry_days"]) + datetime.datetime.now())
            persuasion_obj["workflow_id"] = template.get("workflow", {}).get("name")

        except Exception as e:
            logger.error("Exception is creating persuasion object - " + repr(e))
            raise e
        return persuasion_obj

    @staticmethod
    def update_persuasion(old_persuasion, response):

        new_persuasion = next((p for p in response if p["p_id"] == old_persuasion["p_id"]), None)

        # Case 1st if persuasion doesn't exist
        if not new_persuasion:
            old_persuasion["modified_on"] = str(datetime.datetime.now())
            old_persuasion["latest_event_source"] = new_persuasion["latest_event_source"]
            old_persuasion["status"] = PERSUASION_STATUS[3]
            return old_persuasion

        # Case 2nd If it's expired
        expiry_date = datetime.datetime.strptime(old_persuasion["expiry_date"], DATE_FORMAT)

        new_persuasion["expiry_date"] = old_persuasion["expiry_date"]
        new_persuasion["created_on"] = old_persuasion["created_on"]
        new_persuasion["event_source"] = old_persuasion["event_source"]

        if datetime.datetime.today() > expiry_date:
            new_persuasion["status"] = PERSUASION_STATUS[2]
        else:
            # Case 3rd If it's updated
            new_persuasion["status"] = PERSUASION_STATUS[1]
        return new_persuasion

    @staticmethod
    def get_source_response(source_data):
        response = None
        logger.info("Fetching data source response")
        ds_name = source_data.get('ds_name')
        if ds_name == "mysql":
            query = Utils.format_data(source_data.get("execute", ""), source_data.get("params", dict()))
            # Executing SQL query
            response = json.loads(MYSQL.fetch_data(query))
        elif ds_name == "es":
            query = Utils.evaluate_data(source_data.get("execute", ""), source_data.get("params", dict()))
            es = ElasticSearch(STATIC_DATA_ELASTIC_SEARCH["host"], STATIC_DATA_ELASTIC_SEARCH["protocol"],
                               STATIC_DATA_ELASTIC_SEARCH["port"])
            response = es.get_response(source_data.get("index", ""), query)
        elif ds_name == "lambda":
            package = source_data.get("package", "").replace("/", ".")
            name = source_data.get("execute", "")
            execute = getattr(__import__(package, fromlist=[name]), name)
            response = execute(source_data.get("params"))

        return response
