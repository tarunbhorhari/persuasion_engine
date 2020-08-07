import datetime
import json
import uuid
from datetime import timedelta

from settings.app_constants import KAFKA_SERVER
from utils.kafka_producer import Producer
from utils.utils import Utils


class PersuasionBuilder:
    @staticmethod
    def build_persuasion(body, query_resp, template):
        response = dict()
        response["p_id"] = body.get("p_id", None)
        response["event_source"] = body.get("source", "")
        response["event_created_on"] = body.get("created_on", "")

        data = Utils.template_source_keys_mapping(query_resp, template["source"]["keys_mapping"])
        # TODO - Add groupBy logic here
        response["data"] = data
        response["meta"] = body.get("meta", {})
        response["consumers"] = Utils.render_template_for_wf_consumers(data, template["persuasions"]["consumers"])

        persuasion = PersuasionBuilder.create_persuasion_object(response, template)
        return persuasion

    @classmethod
    def create_persuasion_object(cls, response, template):
        persuasion_obj = dict(response)
        p_id = ""
        # TODO - Optimise the below logic
        if not persuasion_obj["p_id"]:
            for x in template["source"]["group_by"]:
                p_id += "_" + str(response["data"][0].get(x))
            persuasion_obj["p_id"] = "%s_%s%s" % (template["type"], template["sub_type"], p_id)
            persuasion_obj["status"] = "NEW"
        else:
            persuasion_obj["status"] = "UPDATE"
            # TODO -> Add Diff logic (Status will changed based on this)
        persuasion_obj["UUID"] = str(uuid.uuid1())
        persuasion_obj["title"] = template["title"]
        persuasion_obj["type"] = template["type"]
        persuasion_obj["sub_type"] = template["sub_type"]
        persuasion_obj["tags"] = template["tags"]
        persuasion_obj["created_on"] = str(datetime.datetime.now())
        persuasion_obj["modified_on"] = str(datetime.datetime.now())
        persuasion_obj["expiry_date"] = str(timedelta(days=template["expiry_days"]) + datetime.datetime.now())
        persuasion_obj["workflow_id"] = template.get("persuasions", {}).get("wf_name")

        # Publishing persuasion to kafka
        kafka_response = PersuasionBuilder.publish_to_kafka(persuasion_obj)
        return persuasion_obj

    @classmethod
    def publish_to_kafka(cls, persuasion):
        topic = KAFKA_SERVER["TOPIC"]
        producer = Producer()
        return producer.push_message(topic, persuasion["p_id"], json.dumps(persuasion).encode("utf-8"))
