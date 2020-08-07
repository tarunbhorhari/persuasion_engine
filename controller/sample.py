from flask import Blueprint, jsonify

sample = Blueprint('sample', __name__, template_folder='templates')


@sample.route("/")
class Sample:
    @staticmethod
    @sample.route("/<name>", methods=["GET"])
    def index(name):
        return jsonify({"message": "Hey " + name + ", You might looking for something else!!! "})
