import json
from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from mokkiwahti.db_models import Sensor
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
        except ValidationError as e:
            raise BadRequest(description=str(e))

        try: 
            sensor = Sensor()
            sensor.deserialize(request.json)

            db.session.add(sensor)
            db.session.commit()
        except KeyError:
            raise BadRequest
        except IntegrityError:
            raise Conflict(
                description=f"Sensor with name: {sensor.name} already found"
            )
        
        return Response(status=201, headers={
            #"Location": url_for("api.sensoritem", sensor=sensor.name)
            "Location": "Location in progress @TODO"
        })

class SensorItem(Resource):

    def get(self, sensor):
        return Response(json.dumps(sensor.serialize()), 200, mimetype='application/json')

    def put(self):
        pass

    def delete(self, sensor): 
        # @TODO some error handling needed? Sensor is already validated by SensorConverter
        db.session.delete(sensor)
        db.session.commit()
        return Response(
            status=200
        )
