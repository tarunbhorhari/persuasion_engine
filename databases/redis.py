import json
import logging

import redis

from services.persuasion_engine import PersuasionEngine

logger = logging.getLogger("persuasion_engine")


def template_handler(message):
    logger.info("Persuasion templates have changed, updating the latest...")
    try:
        if message:
            PersuasionEngine.TEMPLATES = json.loads(message["data"])
    except Exception as e:
        logger.critical("Redis is not working... " + repr(e))


class CustomRedis:
    cache = None
    pub_sub = None

    def __init__(self, server, port, db):
        self.cache = redis.Redis(host=server, port=port, db=db)
        self.pub_sub = self.cache.pubsub()

    def custom_redis_listener(self, channel_name, call_back):
        self.pub_sub.psubscribe(**{channel_name: call_back})
        self.pub_sub.run_in_thread()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pub_sub.close()
