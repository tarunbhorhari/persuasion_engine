import json
import logging
import signal
from threading import Event

from flask_kafka import FlaskKafka

from services.persuasion_processor import PersuasionProcessor
from settings.app_constants import KAFKA_SERVER

logger = logging.getLogger("persuasion_engine")

INTERRUPT_EVENT = Event()

consumer = FlaskKafka(INTERRUPT_EVENT,
                      bootstrap_servers=KAFKA_SERVER["HOST"],
                      group_id=KAFKA_SERVER["GROUP"]["PERSUASION"])


def listen_kill_server():
    signal.signal(signal.SIGTERM, consumer.interrupted_process)
    signal.signal(signal.SIGINT, consumer.interrupted_process)
    signal.signal(signal.SIGQUIT, consumer.interrupted_process)
    signal.signal(signal.SIGHUP, consumer.interrupted_process)


@consumer.handle(KAFKA_SERVER["TOPIC"]["WATSON"])
def kafka_consumer_listener(con):
    try:
        PersuasionProcessor.process(json.loads(con.value))
        logger.info("consumed {} from persuasion-test2".format(con.value))
    except Exception as e:
        logger.critical("Exception in persuasion kafka consumer - " + repr(e))
