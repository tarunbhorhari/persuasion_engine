import json
import logging

import settings
from utils.utils import Utils

logger = logging.getLogger("persuasion_engine")


class MYSQL:

    @classmethod
    def get_cursor(cls):
        # return mysql.get_db().cursor()
        return settings.mysql.connect().cursor()

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
