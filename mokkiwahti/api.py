from flask import Blueprint
from flask_restful import Api

from mokkiwahti.resources.location import LocationCollection
from mokkiwahti.resources.measurement import MeasurementCollection

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# @TODO Add all remaining resources
api.add_resource(LocationCollection, "/locations/")
