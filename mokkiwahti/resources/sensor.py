from mokkiwahti.db_models import Sensor
from mokkiwahti import db
from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType


class SensorCollection(Resource):

    def get(self):
        pass

    def post(self):
        if not request.json:
            raise UnsupportedMediaType
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

    def get(self):
        pass

    def put(self):
        pass

    def delete(self): 
        pass
