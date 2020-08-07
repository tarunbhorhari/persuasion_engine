from controller.persuasion_engine import persuasion_engine
from controller.sample import sample
from settings import app


class Routes:

    @staticmethod
    def configure_routes():
        app.register_blueprint(sample)
        app.register_blueprint(persuasion_engine)
