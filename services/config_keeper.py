import logging

import requests
import json
from settings.dev import CONFIG_KEEPER_URL

logger = logging.getLogger("persuasion_engine")


class ConfigKeeperAPI:

    @staticmethod
    def get_config(service_name, category):
        """

        :param service_name: CK service name
        :param category: CK category
        :return: Persuasion templates
        """
        logger.info("Fetching templates for " + service_name + " from ConfigKeeper...")
        templates = dict()
        try:
            url = CONFIG_KEEPER_URL + service_name + "&category=[\"" + category + "\"]"
            response = requests.get(url)

            if response.status_code == 200:
                res = json.loads(response.content)
                templates = res.get("data", {}).get(category)

        except Exception as e:
            logger.critical("Error while fetching config from CK")
            raise e
        return templates
