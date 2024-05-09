'''
This file contains ORM classes and methods
'''

from datetime import datetime

import click

from flask.cli import with_appcontext
from mokkiwahti import db

class Location(db.Model):
    '''
    ORM class to represent location data
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    sensors = db.relationship("Sensor",
                              primaryjoin="Location.id == Sensor.location_id",
                              back_populates="location")
    measurements = db.relationship("Measurement",
                                   primaryjoin="Location.id == Measurement.location_id",
                                   back_populates="location")

    @staticmethod
    def get_schema():
        '''
        Returns the JSON schema for Location class
        '''

        return {
            "type": "object",
            "required": ["name"],
            "properties":
            {
                "name": {
                    "description": "Location name",
                    "type": "string"
                }
            }
        }

    def serialize(self, short_form=False):
        '''
        Serializes the Location object
        '''

        serial = {
            "name": self.name,
        }
        if not short_form:
            serial["sensors"] = (self.sensors and
                                 [sensor.serialize(short_form=True)
                                  for sensor in self.sensors])
            serial["measurements"] = (self.measurements and
                                      [measurement.serialize(short_form=True)
                                       for measurement in self.measurements])
        return serial

    def deserialize(self, json):
        '''
        Deserializes the location class from a JSON object
        '''

        self.name = json["name"]


class Sensor(db.Model):
    '''
    ORM class to represent sensor data
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True) # serial code etc?
    location_id = db.Column(db.Integer, db.ForeignKey("location.id", ondelete="SET NULL"))
    sensor_configuration_id = db.Column(db.Integer,
                                        db.ForeignKey("sensor_configuration.id",
                                                      ondelete="SET NULL"))

    location = db.relationship("Location", back_populates="sensors")
    measurements = db.relationship("Measurement", back_populates="sensor")
    sensor_configuration = db.relationship("SensorConfiguration", back_populates="sensor")

    @staticmethod
    def get_schema():
        '''
        Returns the JSON schema for Sensor-class
        '''

        return {
            "type": "object",
            "required": ["name", "sensor_configuration"],
            "properties":
            {
                "name": {
                    "description": "Sensors name",
                    "type": "string"
                },
                "sensor_configuration": {
                    "desciption": "Configuration applied to sensor",
                    "type": "object"
                }
            }
        }

    def serialize(self, short_form=False):
        '''
        Serializes the sensor class
        '''

        serial = {
            "name": self.name,
        }
        if not short_form:
            serial["location"] = self.location and self.location.serialize(short_form=True)
            serial["sensor_configuration"] = (self.sensor_configuration
                                        and self.sensor_configuration.serialize())

        return serial

    def deserialize(self, json):
        '''
        Deserializes the Sensor class from a JSON object.
        '''

        self.name = json["name"]


class Measurement(db.Model):
    '''
    ORM class to represent measurement data
    '''

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id", ondelete="SET NULL"))

    location = db.relationship("Location", back_populates="measurements")
    sensor = db.relationship("Sensor", back_populates="measurements")

    def serialize(self, short_form=False):
        '''
        Serializes the Measurement class
        '''

        serial = {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "timestamp": datetime.isoformat(self.timestamp),
        }
        if not short_form:
            serial["sensor"] = self.sensor and self.sensor.serialize(short_form=True)
            serial["location"] = self.location and self.location.serialize(short_form=True)

        return serial

    def deserialize(self, json):
        '''
        Deserializes the Measurement class from a JSON object
        '''
        self.temperature = json["temperature"]
        self.humidity = json["humidity"]
        self.timestamp = datetime.fromisoformat(json["timestamp"])

    @staticmethod
    def get_schema():
        '''
        Returns the Measurement class JSON Schema
        '''

        schema = {
            "type": "object",
            "required": ["temperature", "humidity", "timestamp"],
            "properties": {
                "temperature": {
                    "description": "Temperature value measured by sensor",
                    "type": "number"
                },
                "humidity": {
                    "description": "Humidity value measured by sensor",
                    "type": "number"
                },
                "timestamp": {
                    "description": "Time value added to measurement",
                    "type": "string",
                    "format": "date-time"
                },
            }
        }
        return schema

class SensorConfiguration(db.Model):
    '''
    ORM class to represent sensor configuration data
    '''

    id = db.Column(db.Integer, primary_key=True)
    interval = db.Column(db.Integer, nullable=False)
    threshold_min = db.Column(db.Float)
    threshold_max = db.Column(db.Float)

    sensor = db.relationship("Sensor", back_populates="sensor_configuration", uselist=False)

    @staticmethod
    def get_schema():
        '''
        Returns the SensorConfiguration class JSON Schema
        '''

        schema = {
            "type": "object",
            "required": ["interval"],
            "properties": {
                "interval": {
                    "description": "Time in between measurements",
                    "type": "number"
                },
                "threshold_min": {
                    "description": "Lower limit to trigger alarm sequence",
                    "type": "number"
                },
                "threshold_max": {
                    "description": "Upper limit to trigger alarm sequence",
                    "type": "number"
                }
            }
        }
        return schema

    def serialize(self):
        '''
        Serializes the SensorConfiguration class
        '''

        return {
            "interval": self.interval,
            "threshold_min": self.threshold_min,
            "threshold_max": self.threshold_max
        }

    def deserialize(self, json):
        '''
        Deserializes the Measurement class from a JSON object
        '''
        self.interval = json["interval"]
        self.threshold_min = json.get("threshold_min")
        self.threshold_max = json.get("threshold_max")


@click.command("init-db")
@with_appcontext
def init_db_command():
    '''
    Callback function for 'init-db' CLI command
    '''
    db.create_all()
