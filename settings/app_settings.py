import logging

import settings
from databases.redis import CustomRedis, template_handler
from services.teams_notification import TeamsNotification
from settings.routes import Routes

logger = logging.getLogger("persuasion_engine")


class Settings:
    @staticmethod
    def initialize_app():
        logger.info("Initialising app level settings")

        Routes.configure_routes()
        redis = CustomRedis(settings.REDIS_SERVER["host"], settings.REDIS_SERVER["port"], settings.REDIS_SERVER["db"])
        redis.custom_redis_listener(settings.TEMPLATE_CHANNEL_NAME, template_handler)

        notification = TeamsNotification("Persuasion Engine is running ....")
        notification.notify()
