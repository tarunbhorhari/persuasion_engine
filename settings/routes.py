import logging

from controller.persuasion_blueprint import persuasion_engine
from settings import app

logger = logging.getLogger("persuasion_engine")


class Routes:

    @staticmethod
    def configure_routes():
        logger.info("Configuring API routes")
        app.register_blueprint(persuasion_engine)
