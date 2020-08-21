import logging

import elasticsearch
from elasticsearch import Elasticsearch

from settings.app_constants import DYNAMIC_DATA_ELASTIC_SEARCH, PERSUASION_ES_INDEX

logger = logging.getLogger("persuasion_engine")


class ElasticSearch:
    es = None

    def __init__(self):
        self.es = Elasticsearch(
            [DYNAMIC_DATA_ELASTIC_SEARCH["host"]],
            http_auth=(),
            scheme=DYNAMIC_DATA_ELASTIC_SEARCH["protocol"],
            port=DYNAMIC_DATA_ELASTIC_SEARCH["port"]
        )

    def get_persuasion(self, persuasion_id):
        persuasion = None
        try:
            es_response = self.es.get(index=PERSUASION_ES_INDEX, id=persuasion_id)
            persuasion = es_response.get("_source")
        except elasticsearch.NotFoundError:
            raise Exception("Invalid persuasion id - " + persuasion_id)
        except Exception as e:
            logger.error("Failed to fetch persuasion from ES - " + repr(e))
        return persuasion
