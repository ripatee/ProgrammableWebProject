import json
from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from mokkiwahti.db_models import Location, Sensor
from mokkiwahti import db
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

class LocationSensorLinker(Resource):

    def put(self, sensor, location):
        location.sensors.append(sensor)
        db.session.commit()
        return Response(status=200)
    
    def delete(self, sensor, location):
        location.sensors.remove(sensor)
        db.session.commit()
        return Response(status=200)
    