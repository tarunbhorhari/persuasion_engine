import datetime
import logging

from flask import jsonify

from databases.elasticsearch import ElasticSearch
from services.kafka_services import KafkaServices
from services.persuasion_engine import PersuasionEngine
from settings.constants import DYNAMIC_DATA_ELASTIC_SEARCH, DATE_FORMAT, PERSUASION_ES_INDEX, DATE_TIME_FORMAT

logger = logging.getLogger("persuasion_engine")


class PersuasionServices:
    @staticmethod
    def create(request_data):
        """
        Common function to create all types of persuasions
        :param request_data:
        :return:
        """
        try:
            meta = dict(push_to_es="true", push_to_inflow="true")
            response = PersuasionEngine.process(request_data)
            KafkaServices.publish_to_kafka(response, meta)
            return response
        except Exception as e:
            raise e

    @staticmethod
    def refresh(request_data, args):
        """
        Common function to refresh all types of persuasions
        :param request_data: Event Packet
        :param args:
        :return: Persuasion
        """
        try:
            p_id = request_data.get("p_id")
            logger.info("Getting updated data of persuasion - " + p_id)
            if not p_id:
                return jsonify(dict(status="failure", error="Please provide persuasion id"))
            es = ElasticSearch(DYNAMIC_DATA_ELASTIC_SEARCH["host"], DYNAMIC_DATA_ELASTIC_SEARCH["protocol"],
                               DYNAMIC_DATA_ELASTIC_SEARCH["port"])
            existing_persuasion = es.get_persuasion(p_id)
            request_data["type"] = existing_persuasion.get("type")
            request_data["sub_type"] = existing_persuasion.get("sub_type")

            # Copying event_packet from existing persuasion
            request_data["data"] = existing_persuasion["meta"].get("event_packet")
            response = PersuasionEngine.process(request_data)

            persuasion = PersuasionEngine.update_persuasion(existing_persuasion, response)
            KafkaServices.publish_to_kafka([persuasion], args)
            return persuasion
        except Exception as e:
            raise e

    @staticmethod
    def get_persuasions_request_from_es(args):
        """
        Generating persuasions request for bulk refresh
        :param args:
        :return:
        """
        today = datetime.datetime.now()
        try:
            logger.info("Refreshing persuasions on scheduled basis ")
            start_date = datetime.datetime.strptime(args.get("start_date"), DATE_FORMAT).strftime(
                DATE_TIME_FORMAT) if args.get("start_date") else str(today.strftime(DATE_TIME_FORMAT))

            end_date = datetime.datetime.strptime(args.get("end_date"), DATE_FORMAT).strftime(
                DATE_TIME_FORMAT) if args.get("end_date") else str(today.strftime(DATE_TIME_FORMAT))

            query = {"_source": ["p_id", "type", "sub_type"],
                     "query": {"bool": {"must": [{"term": {"type": {"value": args["type"]}}},
                                                 {"term": {"sub_type": {"value": args["sub_type"]}}},
                                                 {"range": {"created_on": {"gte": start_date, "lte": end_date}
                                                            }}]}}}
            es = ElasticSearch(DYNAMIC_DATA_ELASTIC_SEARCH["host"], DYNAMIC_DATA_ELASTIC_SEARCH["protocol"],
                               DYNAMIC_DATA_ELASTIC_SEARCH["port"])
            response = es.get_response(PERSUASION_ES_INDEX, query)
            return response
        except Exception as e:
            raise e
