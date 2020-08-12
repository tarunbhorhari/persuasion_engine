import json
import logging

from flaskext.mysql import MySQL

from settings import app
from settings.app_constants import DATABASES
from utils.utils import Utils

logger = logging.getLogger("persuasion_engine")


class MYSQL:
    mysql = MySQL()

    @staticmethod
    def initialize_sql_config():
        app.config['MYSQL_DATABASE_USER'] = DATABASES['default']['USER']
        app.config['MYSQL_DATABASE_PASSWORD'] = DATABASES['default']['PASSWORD']
        app.config['MYSQL_DATABASE_DB'] = DATABASES['default']['NAME']
        app.config['MYSQL_DATABASE_HOST'] = DATABASES['default']['HOST']
        MYSQL.mysql.init_app(app)

    @classmethod
    def get_cursor(cls):
        return MYSQL.mysql.get_db().cursor()

    @staticmethod
    def fetch_data(query):
        try:
            cursor = MYSQL.get_cursor()
            cursor.execute(query)
            row_headers = [x[0] for x in cursor.description]  # This will extract the headers
            data = cursor.fetchall()
            cursor.close()
            response = Utils.convert_tuple_to_dict(row_headers, data)
            return json.dumps(response, default=Utils.datetime_serializer())
        except Exception as e:
            logger.critical("Exception in executing SQL query : %s - %s " % (query, repr(e)))
            return json.dumps(dict())
