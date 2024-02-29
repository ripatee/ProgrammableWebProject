from mokkiwahti.db_models import Sensor, Measurement, Location
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter

# Placeholder file for util functions and classes, ex. Converter classes

class SensorConverter(BaseConverter):
    
    def to_python(self, value):
        db_sensor = Sensor.query.filter_by(name=value).first()
        if db_sensor is None:
            raise NotFound
        return db_sensor
        
    def to_url(self, value):
        return value.name
    
class MeasurementConverter(BaseConverter):

    def to_python(self, value):
        db_measurement = Measurement.query.filter_by(id=value).first()
        if db_measurement is None:
            raise NotFound
        return db_measurement

    def to_url(self, value):
        return str(value.id)

class LocationConverter(BaseConverter):

    def to_python(self, value):
        db_location = Location.query.filter_by(name=value).first()
        if db_location is None:
            raise NotFound
        return db_location

    def to_url(self, value):
        return value.name
    