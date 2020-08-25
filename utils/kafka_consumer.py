import json
import logging
import signal
from threading import Event

from flask_kafka import FlaskKafka

from services.persuasion_builder import PersuasionBuilder
from services.persuasion_processor import PersuasionProcessor
from settings.constants import KAFKA_SERVER

logger = logging.getLogger("persuasion_engine")

INTERRUPT_EVENT = Event()

consumer = FlaskKafka(INTERRUPT_EVENT,
                      bootstrap_servers=KAFKA_SERVER["HOST"],
                      group_id=KAFKA_SERVER["GROUP"]["PERSUASION"],
                      enable_auto_commit=False,
                      request_timeout_ms=30000)


def listen_kill_server():
    signal.signal(signal.SIGTERM, consumer.interrupted_process)
    signal.signal(signal.SIGINT, consumer.interrupted_process)
    signal.signal(signal.SIGQUIT, consumer.interrupted_process)
    signal.signal(signal.SIGHUP, consumer.interrupted_process)


@consumer.handle(KAFKA_SERVER["TOPIC"]["PERSUASION"])
def kafka_consumer_listener(con):
    try:
        data = json.loads(con.value)
        response = PersuasionProcessor.process(data)
        logger.info("consumed {} from persuasion-test2".format(con.value))
        # Publishing each persuasion to kafka
        meta = dict(push_to_es="true", push_to_inflow="true")
        response = PersuasionProcessor.process(data)
        PersuasionBuilder.publish_to_kafka(response, meta)
    except Exception as e:
        logger.critical("Exception in persuasion kafka consumer - " + repr(e))
