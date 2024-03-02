'''
File for utility functions and classes, ex. Converter classes
'''

from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter
from mokkiwahti.db_models import Sensor, Measurement, Location

class SensorConverter(BaseConverter):
    '''
    Converts sensor from URL to python object, and vice versa.
    Raises NotFound if the sensor is not found from the database
    '''

    def to_python(self, value):
        db_sensor = Sensor.query.filter_by(name=value).first()
        if db_sensor is None:
            raise NotFound
        return db_sensor

    def to_url(self, value):
        return value.name

class MeasurementConverter(BaseConverter):
    '''
    Converts measurement string from URL to python object, and vice versa.
    Raises NotFound if the measurement is not found
    '''

    def to_python(self, value):
        db_measurement = Measurement.query.filter_by(id=value).first()
        if db_measurement is None:
            raise NotFound
        return db_measurement

    def to_url(self, value):
        return str(value.id)

class LocationConverter(BaseConverter):
    '''
    Converts location string from URL to python object, and vice versa.
    Raises NotFound if the location is not found
    '''

    def to_python(self, value):
        db_location = Location.query.filter_by(name=value).first()
        if db_location is None:
            raise NotFound
        return db_location

    def to_url(self, value):
        return value.name
