'''
API resources related to Sensors
'''

import json
from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

from mokkiwahti.db_models import Sensor, SensorConfiguration
from mokkiwahti import db

class SensorCollection(Resource):
    '''
    SensorCollection resource. Supports GET and POST methods.
    '''

    def get(self):
        '''
        Returns all locations as a HTTP Response object that contains sensor
        information as a JSON object
        '''

        sensors = []
        for sensor in Sensor.query.all():
            sensors.append(sensor.serialize())

        return Response(json.dumps(sensors), 200, mimetype='application/json')

    def post(self):
        '''
        Add new sensor to database.

        Checks that the input is JSON and validates it against the schema
        Deserializes the Sensor object from JSON
        Adds sensor to database
        Sends response containing location to the newly added sensor
        '''

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Sensor.get_schema())
            validate(request.json["sensor_configuration"], SensorConfiguration.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        try:
            sensor = Sensor()
            sensor.deserialize(request.json)

            sensor_configuration = SensorConfiguration()
            sensor_configuration.deserialize(request.json["sensor_configuration"])

            sensor.sensor_configuration = sensor_configuration

            db.session.add(sensor)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                description=f"Sensor with name: {sensor.name} already found"
            ) from e

        return Response(status=201, headers={
            "Location": url_for("api.sensoritem", sensor=sensor)
        })

class SensorItem(Resource):
    '''
    Sensor item resource. Supports GET, PUT and DELETE methods.
    '''

    def get(self, sensor):
        '''
        Returns a Response containing a specific sensor item
        '''

        return Response(json.dumps(sensor.serialize()), 200, mimetype='application/json')

    def put(self, sensor):
        '''
        Modifies an existing sensor resource

        Checks that the input is a JSON and validates it agains the schema
        Adds it to the database and returns a Response object with status code 201
        '''

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Sensor.get_schema())
            validate(request.json["sensor_configuration"], SensorConfiguration.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        sensor.deserialize(request.json)
        sensor.sensor_configuration.deserialize(request.json["sensor_configuration"])
        db.session.commit()

        return Response(status=200, headers={
            "Location": "Location in progress @TODO"
        })

    def delete(self, sensor):
        '''
        Deletes a specific Sensor item from the database

        Returns a Response object with status code 200
        '''

        db.session.delete(sensor)
        db.session.commit()
        return Response(
            status=200
        )
