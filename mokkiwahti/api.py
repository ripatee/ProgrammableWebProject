from flask import Blueprint
from flask_restful import Api

from mokkiwahti.resources.location import LocationCollection
from mokkiwahti.resources.measurement import MeasurementCollection

# File where all API-related stuff lives, ex. routing the resources

# Register blueprint for API. This ensures that all routes starts with "/api" and we don't need 
# to rewrite it all the time. Also makes it easier to add another functionalities (ex. admin view)
# in future
api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# @TODO Add all remaining resources
api.add_resource(LocationCollection, "/locations/")
