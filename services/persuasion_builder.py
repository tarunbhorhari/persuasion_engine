import datetime
import logging
import uuid
from datetime import timedelta
from itertools import groupby
from operator import itemgetter

from elasticsearch_dsl import Search

from settings.app_constants import ES_CLIENT_DYNAMIC, PERSUASION_ES_INDEX
from utils.utils import Utils

logger = logging.getLogger("persuasion_engine")


class PersuasionBuilder:
    @staticmethod
    def build_persuasion(body, query_resp, template):
        persuasions = []
        try:
            response = dict()

            response["p_id"] = body.get("p_id", None)

            if response["p_id"]:
                # Getting persuasion from ES
                search_obj = Search(using=ES_CLIENT_DYNAMIC, index=PERSUASION_ES_INDEX)
                search_obj.query("match", _id=response["p_id"])
                es_response = search_obj.execute()
                existing_persuasion = es_response[0].to_dict()
                # TODO - Remove below line and think through diff logic
                persuasions.append(existing_persuasion)
                return persuasions

            response["event_source"] = body.get("source", "")
            response["event_created_on"] = body.get("created_on", "")
            response["meta"] = body.get("meta", {})

            # Initializing query response data to key mapping
            data = Utils.template_source_keys_mapping(query_resp, template["source"]["keys_mapping"])
            response["consumers"] = Utils.render_template_for_wf_consumers(data, template["persuasions"]["consumers"])

            # Grouping logic
            group = template.get("source", {}).get("group_by")
            grouper = itemgetter(*group)

            for k, v in groupby(data, grouper):
                response["data"] = list(v)
                persuasion = PersuasionBuilder.create_persuasion_object(response, template)
                persuasions.append(persuasion)
                # TODO -> Add Diff logic (Status will changed based on this)

        except Exception as e:
            logger.error("Exception while building persuasions" + repr(e))
        return persuasions

    @classmethod
    def create_persuasion_object(cls, response, template):
        persuasion_obj = dict(response)
        try:
            p_id = ""
            # TODO - Optimise the below logic
            if not persuasion_obj["p_id"]:
                for x in template["source"]["group_by"]:
                    p_id += "_" + str(response["data"][0].get(x))
                persuasion_obj["p_id"] = "%s_%s%s" % (template["type"], template["sub_type"], p_id)
                persuasion_obj["status"] = "new"
            else:
                persuasion_obj["status"] = "updated"

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

        return persuasion_obj
