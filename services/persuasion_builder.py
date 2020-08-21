import datetime
import json
import logging
import uuid
from datetime import timedelta
from itertools import groupby
from operator import itemgetter

from settings.app_constants import KAFKA_SERVER
from utils.kafka_producer import Producer
from utils.utils import Utils

logger = logging.getLogger("persuasion_engine")


class PersuasionBuilder:
    @staticmethod
    def build_persuasion(body, query_resp, template):
        persuasions = []
        try:
            response = dict()
            response["p_id"] = body.get("p_id", None)
            response["event_source"] = body.get("source", "")
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
                persuasion = PersuasionBuilder.create_persuasion_object(response, template)
                persuasions.append(persuasion)

        except Exception as e:
            logger.error("Exception while building persuasions" + repr(e))
        return persuasions

    @classmethod
    def create_persuasion_object(cls, response, template):
        persuasion_obj = dict(response)
        try:
            p_id = ""
            # TODO - Optimise the below logic
            for x in template["source"]["group_by"]:
                p_id += "_" + str(response["data"][0].get(x))
            persuasion_obj["p_id"] = "%s_%s%s" % (template["type"], template["sub_type"], p_id)
            persuasion_obj["status"] = "NEW"

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

    @classmethod
    def publish_to_watson_kafka(cls, persuasion):
        kafka_resp = dict()
        try:
            topic = KAFKA_SERVER["TOPIC"]["WATSON"]
            producer = Producer()
            key = persuasion["p_id"].encode("utf-8")
            value = json.dumps(persuasion).encode("utf-8")
            kafka_resp = producer.push_message(topic, key, value)
        except Exception as e:
            logger.critical("Exception while pushing persuasion to kafka - " + repr(e))
        return kafka_resp

    @classmethod
    def publish_to_inflow_kafka(cls, persuasion):
        kafka_resp = dict()
        try:
            topic = KAFKA_SERVER["TOPIC"]["INFLOW"]
            producer = Producer()
            key = persuasion["p_id"].encode("utf-8")
            value = json.dumps(persuasion).encode("utf-8")
            kafka_resp = producer.push_message(topic, key, value)
        except Exception as e:
            logger.critical("Exception while pushing persuasion to kafka - " + repr(e))
        return kafka_resp

    @staticmethod
    def publish_to_kafka(response, meta):
        for persuasion in response:
            if meta.get("push_to_es", "false") == "true":
                watson_kafka_response = PersuasionBuilder.publish_to_watson_kafka(persuasion)
                logger.info(watson_kafka_response)
            if meta.get("push_to_inflow", "false") == "true":
                inflow_kafka_response = PersuasionBuilder.publish_to_inflow_kafka(persuasion)
                logger.info(inflow_kafka_response)
