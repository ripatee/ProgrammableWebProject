from flask import Response
from flask_restful import Resource

from mokkiwahti import db


class LocationSensorLinker(Resource):

    def put(self, sensor, location):
        location.sensors.append(sensor)
        db.session.commit()
        return Response(status=200)

    def delete(self, sensor, location):
        location.sensors.remove(sensor)
        db.session.commit()

        return Response(status=200)
