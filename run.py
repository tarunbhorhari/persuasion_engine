import logging

from settings import app
from settings.app_settings import Settings
from utils.kafka_consumer import listen_kill_server, consumer
from settings.dev import FLASK

logger = logging.getLogger("persuasion_engine")

if __name__ == "__main__":
    logger.info("Generic Persuasion Engine is Running..... ")
    try:
        Settings.initialize_app()
        consumer.run()
        listen_kill_server()
        app.run(host=FLASK["host"], port=FLASK["port"])
        logger.info("Shutting down Generic Persuasion Engine...")
    except Exception as e:
        logger.critical("Error while starting/stopping persuasion engine " + repr(e))
