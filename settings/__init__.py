import logging
import os

from flask import Flask
from flaskext.mysql import MySQL

from settings.base import *

logging.basicConfig(filename="logs/persuasion_engine.log", level=logging.INFO)
ENVIRONMENT = os.environ.get("CURRENT_ENV", "prod")
# ENVIRONMENT = "dev"

# <<<<<<<<<--------- Loading settings as per environment --------->>>>>>>>>>
if ENVIRONMENT.lower() == "dev":
    try:
        from settings.dev import *
    except:
        pass
elif ENVIRONMENT.lower() == "staging":
    try:
        from settings.staging import *
    except:
        pass
elif ENVIRONMENT.lower() == "prod":
    try:
        from settings.prod import *
    except:
        pass

# <<<<<<<<<<<-------------- Setting up FLASK App  -------------->>>>>>>>>>>>
app = Flask(app_name)

app.config["MYSQL_DATABASE_USER"] = DATABASES["default"]["USER"]
app.config["MYSQL_DATABASE_PASSWORD"] = DATABASES["default"]["PASSWORD"]
app.config["MYSQL_DATABASE_DB"] = DATABASES["default"]["NAME"]
app.config["MYSQL_DATABASE_HOST"] = DATABASES["default"]["HOST"]

mysql = MySQL()
mysql.init_app(app)
