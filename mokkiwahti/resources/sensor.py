import json
from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from mokkiwahti.db_models import Sensor, SensorConfiguration
from mokkiwahti import db
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType


class SensorCollection(Resource):

    def get(self):
        sensors = []
        for sensor in Sensor.query.all():
            sensors.append(sensor.serialize())
        
        return Response(json.dumps(sensors), 200, mimetype='application/json')

    def post(self):
        if not request.json:
            raise UnsupportedMediaType
        
        try:
            validate(request.json, Sensor.get_schema())
            validate(request.json["sensor_configuration"], SensorConfiguration.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

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
            )
        
        return Response(status=201, headers={
            "Location": url_for("api.sensoritem", sensor=sensor)
        })

class SensorItem(Resource):

    def get(self, sensor):
        return Response(json.dumps(sensor.serialize()), 200, mimetype='application/json')

    def put(self, sensor):
        if not request.json:
            raise UnsupportedMediaType
        
        try:
            validate(request.json, Sensor.get_schema())
            validate(request.json["sensor_configuration"], SensorConfiguration.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        
        sensor.deserialize(request.json)
        sensor.sensor_configuration.deserialize(request.json["sensor_configuration"])
        db.session.commit()

        return Response(status=200, headers={
            "Location": "Location in progress @TODO"
        })

    def delete(self, sensor): 
        # @TODO some error handling needed? Sensor is already validated by SensorConverter
        db.session.delete(sensor)
        db.session.commit()
        return Response(
            status=200
        )
