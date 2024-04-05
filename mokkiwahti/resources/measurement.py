'''
API resources related to measurements
'''

import json
from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError, Draft7Validator

from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from mokkiwahti.db_models import Measurement, Location, Sensor
from mokkiwahti import db

class MeasurementCollection(Resource):
    '''
    MeasurementCollection resourse. Supports GET and POST methods
    '''

    def get(self, location=None, sensor=None):
        '''
        Returns specific measurement by location or sensor.

        Responses:
        200 - OK
        '''

        measurements = []
        # Check if measurements are querried by location or by sensor
        if location is not None:
            measurements_db = (Measurement
                               .query
                               .join(Location)
                               .filter(Location.name == location.name)
                               .all())
        elif sensor is not None:
            measurements_db = (Measurement
                               .query
                               .join(Sensor)
                               .filter(Sensor.name == sensor.name)
                               .all())
        for measurement in measurements_db:
            measurements.append(measurement.serialize())

        return Response(json.dumps(measurements), 200, mimetype='application/json')


    def post(self, sensor):
        '''
        Add new measurement to the database

        Checks that the input is JSON and validates it agains the schema
        Deserializes the Measurement object from JSON
        Add measuerement to the database
        Sends response containing location to the newly added measurements

        Possible responses:
        201 - Created
        400 - Bad request
        415 - Unsupported media type
        '''

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json,
                     Measurement.get_schema(),
                     format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        # @TODO Is error handling needed here?
        measurement = Measurement()
        measurement.deserialize(request.json)
        measurement.sensor = sensor
        measurement.location = sensor.location

        db.session.add(measurement)
        db.session.commit()

        return Response(status=201, headers={
            "Location:": url_for("api.measurementitem", measurement=measurement)
        })

class MeasurementItem(Resource):
    '''
    Measure item resource. Supports GET, PUT and DELETE.
    '''

    def get(self, measurement):
        '''
        Returns a Response object containin a specific measurement item

        Responses:
        200 - OK
        '''

        return Response(json.dumps(measurement.serialize(),
                                   status=200,
                                   mimetype='application/json'))

    def put(self, measurement):
        '''
        Modifies an existing measurement resource

        Checks that the input is a JSON and validates it agains the schema
        Adds it to the database and returns a Response object

        Responses:
        200 - OK
        400 - Bad Request
        415 - Unsupported media type
        '''

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json,
                     Measurement.get_schema(),
                     format_checker=Draft7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        measurement.deserialize(request.json)
        db.session.commit()

        return Response(status=200, headers={
            "Location": url_for("api.measurementitem", measurement=measurement)
        })

    def delete(self, measurement):
        '''
        Deletes a specific location item from the database

        Returns a Response object with status code 200

        Responses:
        200 - OK
        '''

        db.session.delete(measurement)
        db.session.commit()
        return Response(
            status=200
        )
