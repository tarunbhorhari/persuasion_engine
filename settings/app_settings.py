import logging

from databases.redis import CustomRedis, template_handler
from services.teams_notification import TeamsNotification
from settings.constants import REDIS_SERVER, TEMPLATE_CHANNEL_NAME
from settings.routes import Routes

logger = logging.getLogger("persuasion_engine")


class Settings:
    @staticmethod
    def initialize_app():
        logger.info("Initialising app level settings")

        Routes.configure_routes()
        redis = CustomRedis(REDIS_SERVER["host"], REDIS_SERVER["port"], REDIS_SERVER["db"])
        redis.custom_redis_listener(TEMPLATE_CHANNEL_NAME, template_handler)

        notification = TeamsNotification("Persuasion Engine is running ....")
        notification.notify()
