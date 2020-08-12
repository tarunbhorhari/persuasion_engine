import logging

from settings import app
from settings.app_settings import Settings

logger = logging.getLogger("persuasion_engine")
if __name__ == "__main__":
    logger.info("Generic Persuasion Engine is Running..... ")
    Settings.initialize_app()
    app.run()
    logger.info("Shutting down Generic Persuasion Engine...")
