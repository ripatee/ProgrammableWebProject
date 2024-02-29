import json
from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from mokkiwahti.db_models import Measurement
from mokkiwahti import db
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

class MeasurementCollection(Resource):

    def get(self):
        pass

    def post(self):
        pass

class MeasurementItem(Resource):

    def get(self):
        pass

    def put(self):
        pass
    
    def delete(self):
        pass