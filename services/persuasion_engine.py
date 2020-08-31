import datetime
import json
import logging
import uuid
from datetime import timedelta
from itertools import groupby
from operator import itemgetter

from databases.mysql import MYSQL
from services.config_keeper import ConfigKeeperAPI
from settings.constants import PERSUASION_STATUS, DATE_FORMAT, CONFIG_KEEPER_SERVICE_NAME, CONFIG_KEEPER_CATEGORY, \
    TEMPLATE_CHOICES
from utils.utils import Utils

logger = logging.getLogger("persuasion_engine")


class PersuasionEngine:
    TEMPLATES = ConfigKeeperAPI.get_config(CONFIG_KEEPER_SERVICE_NAME, CONFIG_KEEPER_CATEGORY)

    @staticmethod
    def process(request_data):
        # base_path = "/Users/tarun.bhorhari/projects/persuasion_engine/templates/"
        # file_path = "%s%s_%s.json" % (base_path, request_data.get("type"), request_data.get("sub_type"))
        # TODO - Add request data validations if any

        sub_type = request_data.get("sub_type")
        persuasion_type = request_data.get("type")
        templates = [PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type))] if sub_type else [
            PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type)) for sub_type in
            TEMPLATE_CHOICES[persuasion_type] if PersuasionEngine.TEMPLATES.get("%s_%s" % (persuasion_type, sub_type))]

        persuasion_resp = []
        logger.info("Processing persuasion config")
        # with open(file_path) as persuasion_template:
        for template in templates:
            #template = json.load(persuasion_template)
            source_data = template.get("source", {})
            Utils.initialize_mapping(source_data.get("params", dict()), request_data.get("data"))
            logger.info("Building data source query")
            query = Utils.query_builder(source_data.get("execute", ""),
                                        source_data.get("params", dict()), source_data.get('ds_name'))
            try:
                # Executing SQL query
                query_response = json.loads(MYSQL.fetch_data(query))

                persuasion_resp = PersuasionEngine.build_persuasion(request_data, query_response, template)
            except Exception as e:
                logger.error("Exception while processing persuasion config - " + repr(e))
                raise e

        return persuasion_resp

    @staticmethod
    def build_persuasion(body, query_resp, template):
        persuasions = []
        try:
            response = dict()
            response["p_id"] = body.get("p_id", None)
            response["event_source"] = body.get("source", "")
            response["latest_event_source"] = body.get("source", "")
            response["event_created_on"] = body.get("created_on", "")
            response["meta"] = body.get("meta", {})
            response["meta"].update(dict(event_packet=body.get("data", {})))

            # Initializing query response data to key mapping
            data = Utils.template_source_keys_mapping(query_resp, template["source"]["keys_mapping"])
            response["consumers"] = Utils.render_template_for_wf_consumers(data, template["persuasions"]["consumers"])

            # Grouping logic
            group = template.get("source", {}).get("group_by")
            grouper = itemgetter(*group)

            for k, v in groupby(data, grouper):
                response["data"] = list(v)
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

            p_id = "_".join([str(response["data"][0].get(x)) for x in list(template["source"]["group_by"])])
            persuasion_obj["p_id"] = "%s_%s_%s" % (template["type"], template["sub_type"], p_id)
            persuasion_obj["status"] = PERSUASION_STATUS[0]

            persuasion_obj["UUID"] = str(uuid.uuid1())
            persuasion_obj["title"] = template["title"]
            persuasion_obj["type"] = template["type"]
            persuasion_obj["sub_type"] = template["sub_type"]
            persuasion_obj["tags"] = template["tags"]
            persuasion_obj["created_on"] = str(datetime.datetime.now())
            persuasion_obj["modified_on"] = str(datetime.datetime.now())
            persuasion_obj["expiry_date"] = str(timedelta(days=template["expiry_days"]) + datetime.datetime.now())
            persuasion_obj["workflow_id"] = template.get("persuasions", {}).get("wf_name")
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
