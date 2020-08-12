import logging

from controller.persuasion_engine import persuasion_engine
from controller.sample import sample
from settings import app

logger = logging.getLogger("persuasion_engine")


class Routes:

    @staticmethod
    def configure_routes():
        logger.info("Configuring API routes")
        app.register_blueprint(sample)
        app.register_blueprint(persuasion_engine)
