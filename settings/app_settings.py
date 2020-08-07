from databases.mysql import MYSQL
from settings.routes import Routes


class Settings:
    @staticmethod
    def initialize_app():
        Routes.configure_routes()
        MYSQL.initialize_sql_config()
