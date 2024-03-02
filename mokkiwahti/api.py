from flask import Blueprint
from flask_restful import Api

from mokkiwahti.resources.location import LocationCollection, LocationItem
from mokkiwahti.resources.measurement import MeasurementCollection, MeasurementItem
from mokkiwahti.resources.sensor import SensorCollection, SensorItem
from mokkiwahti.resources.linker import LocationSensorLinker

# File where all API-related stuff lives, ex. routing the resources

# Register blueprint for API. This ensures that all routes starts with "/api" and we don't need
# to rewrite it all the time. Also makes it easier to add another functionalities (ex. admin view)
# in future
api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# @TODO Add all remaining resources

# As we are using blueprint, the actual URI will be /api/locations/ etc.
api.add_resource(LocationCollection, "/locations/")
api.add_resource(LocationItem, "/locations/<location:location>/")
api.add_resource(SensorCollection, "/sensors/")
api.add_resource(SensorItem, "/sensors/<sensor:sensor>/")
api.add_resource(MeasurementCollection,
                 "/sensors/<sensor:sensor>/measurements/",
                 "/locations/<location:location>/measurements/")
api.add_resource(MeasurementItem, "/measurement/<measurement:measurement>")
api.add_resource(LocationSensorLinker, "/locations/<location:location>/link/sensors/<sensor:sensor>/")
