import json
import logging

import elasticsearch
from elasticsearch import Elasticsearch

import settings

logger = logging.getLogger("persuasion_engine")


class ElasticSearch:
    es = None

    def __init__(self, host, protocol, port):
        self.es = Elasticsearch(
            [host],
            http_auth=(),
            scheme=protocol,
            port=port
        )

    def get_persuasion(self, persuasion_id):
        persuasion = None
        try:
            es_response = self.es.get(index=settings.PERSUASION_ES_INDEX, id=persuasion_id)
            persuasion = es_response.get("_source")
        except elasticsearch.NotFoundError:
            raise Exception("Invalid persuasion id - " + persuasion_id)
        except Exception as e:
            logger.error("Failed to fetch persuasion from ES - " + repr(e))
        return persuasion

    def get_response(self, index, query):
        response = list()
        try:
            es_response = self.es.search(index=index, body=json.dumps(query))
            if es_response['hits']['hits']:
                response_hits = es_response['hits']['hits']
                response = [o['_source'] for o in response_hits]
        except elasticsearch.NotFoundError:
            raise Exception("Invalid query - " + query)
        except Exception as e:
            logger.error("Failed to fetch query response from ES - " + repr(e))
        return response
