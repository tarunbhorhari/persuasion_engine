import logging

from flask import Flask
from flaskext.mysql import MySQL

from settings.dev import app_name, DATABASES

logging.basicConfig(filename="logs/persuasion_engine.log", level=logging.INFO)

app = Flask(app_name)

app.config['MYSQL_DATABASE_USER'] = DATABASES['default']['USER']
app.config['MYSQL_DATABASE_PASSWORD'] = DATABASES['default']['PASSWORD']
app.config['MYSQL_DATABASE_DB'] = DATABASES['default']['NAME']
app.config['MYSQL_DATABASE_HOST'] = DATABASES['default']['HOST']

mysql = MySQL()
mysql.init_app(app)
