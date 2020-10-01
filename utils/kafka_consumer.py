import json
import logging
import signal
from threading import Event

from flask_kafka import FlaskKafka

import settings
from services.persuasion_services import PersuasionServices

logger = logging.getLogger("persuasion_engine")

INTERRUPT_EVENT = Event()

consumer = FlaskKafka(INTERRUPT_EVENT,
                      bootstrap_servers=settings.KAFKA_SERVER["host"],
                      group_id=settings.KAFKA_SERVER["group"]["persuasion"],
                      enable_auto_commit=False,
                      request_timeout_ms=30000)


def listen_kill_server():
    signal.signal(signal.SIGTERM, consumer.interrupted_process)
    signal.signal(signal.SIGINT, consumer.interrupted_process)
    signal.signal(signal.SIGQUIT, consumer.interrupted_process)
    signal.signal(signal.SIGHUP, consumer.interrupted_process)


@consumer.handle(settings.KAFKA_SERVER["topic"]["persuasion"])
def kafka_consumer_listener(con):
    """
     Watson kafka consumer to create persuasions on real time
    :param con: Event packet
    :return: None
    """
    try:
        data = json.loads(con.value)
        response = PersuasionServices.create(data)
        logger.info("consumed {} from persuasion-test2".format(con.value))

    except Exception as e:
        logger.critical("Exception in persuasion kafka consumer - " + repr(e))
