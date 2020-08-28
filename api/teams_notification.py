import json
import logging

import requests

from settings.constants import TEAMS_NOTIFICATION_URL

logger = logging.getLogger("persuasion_engine")


class TeamsNotification:
    facts = None
    title = None
    URL = TEAMS_NOTIFICATION_URL
    HEADERS = {
        'Content-Type': 'application/json',
    }

    def __init__(self, title):
        self.facts = []
        self.title = title

    def append(self, key, value):
        self.facts.append(dict(name=key, value=value))

    def notify(self):
        logger.info("Sending notifications to teams")
        data = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Persuasion is scheduled",
            "sections": [{
                "activityTitle": self.title,
                "activitySubtitle": "",
                "activityImage": "https://cwiki.apache.org/confluence/download/attachments/30737784/oozie_47x200.png?version=1&modificationDate=1349284899000&api=v29",
                "facts": self.facts,
                "markdown": True
            }]
        }

        try:
            response = requests.post(self.URL, headers=self.HEADERS, data=json.dumps(data))
            logger.log("Successfully send notification to teams")
        except Exception as e:
            logger.error("Error while sending notification to teams - " + repr(e))
