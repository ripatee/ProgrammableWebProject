import json
from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError, draft7_format_checker

from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from mokkiwahti.db_models import Measurement, Location, Sensor
from mokkiwahti import db

class MeasurementCollection(Resource):

    def get(self, location=None, sensor=None):
        measurements = []
        # Check if measurements are querried by location or by sensor
        if location is not None:
            measurements_db = Measurement.query.join(Location).filter(Location.name == location.name).all()
        elif sensor is not None:
            measurements_db = Measurement.query.join(Sensor).filter(Sensor.name == sensor.name).all()

        for measurement in measurements_db:
            measurements.append(measurement.serialize())

        return Response(json.dumps(measurements), 200, mimetype='application/json')


    def post(self, sensor):
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Measurement.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

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

    def get(self, measurement):
        return Response(json.dumps(measurement.serialize(), 200, mimetype='application/json'))

    def put(self, measurement):
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Measurement.get_schema(), format_checker=draft7_format_checker)
        except ValidationError as e:
            raise BadRequest(description=str(e))

        measurement.deserialize(request.json)
        db.session.commit()

        return Response(status=200, headers={
            "Location": url_for("api.measurementitem", measurement=measurement)
        })

    def delete(self, measurement):
        db.session.delete(measurement)
        db.session.commit()
        return Response(
            status=200
        )
