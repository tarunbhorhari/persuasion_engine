import logging

from databases.mysql import MYSQL
from settings.routes import Routes

logger = logging.getLogger("persuasion_engine")


class Settings:
    @staticmethod
    def initialize_app():
        logger.info("Initialising app level settings")
        Routes.configure_routes()
        MYSQL.initialize_sql_config()
