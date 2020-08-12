import logging

from flask import Flask

from settings.app_constants import app_name

logging.basicConfig(filename="logs/persuasion_engine.log", level=logging.INFO)
app = Flask(app_name)
