import json
import logging

from databases.mysql import MYSQL
from services.persuasion_builder import PersuasionBuilder
from utils.utils import Utils

logger = logging.getLogger("persuasion_engine")


class PersuasionProcessor:

    @staticmethod
    def process(request_data):
        base_path = "/Users/tarun.bhorhari/projects/persuasion_engine/templates/"
        file_path = "%s%s_%s.json" % (base_path, request_data.get("type"), request_data.get("sub_type"))
        # TODO - Add persuasion config variable here and fetch config accordingly
        # TODO - Add request data validation
        persuasion_resp = []
        logger.info("Processing persuasion config")
        with open(file_path) as persuasion_template:
            template = json.load(persuasion_template)
            source_data = template.get("source", {})
            Utils.initialize_mapping(source_data.get("params", dict()), request_data.get("data"))
            logger.info("Building data source query")
            query = Utils.query_builder(source_data.get("execute", ""),
                                        source_data.get("params", dict()), source_data.get('ds_name'))
            try:
                # Executing SQL query
                query_response = json.loads(MYSQL.fetch_data(query))

                persuasion_resp = PersuasionBuilder.build_persuasion(request_data, query_response, template)
            except Exception as e:
                logger.error("Exception while processing persuasion config - " + repr(e))

        return persuasion_resp
