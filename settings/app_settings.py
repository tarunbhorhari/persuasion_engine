import logging

from services.teams_notification import TeamsNotification
from settings.routes import Routes

logger = logging.getLogger("persuasion_engine")


class Settings:
    @staticmethod
    def initialize_app():
        logger.info("Initialising app level settings")
        Routes.configure_routes()
        notification = TeamsNotification("Persuasion Engine is running ....")
        notification.notify()
