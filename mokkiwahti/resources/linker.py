'''
API resources related to LocationSensorLinker
'''

from flask import Response
from flask_restful import Resource

from mokkiwahti import db


class LocationSensorLinker(Resource):
    '''
    LocationCollection resource. Supports PUT and DELETE methods.
    '''

    def put(self, sensor, location):
        '''
        Links Locations and Sensors.

        Returns Response object with status code 200
        '''

        location.sensors.append(sensor)
        db.session.commit()
        return Response(status=200)

    def delete(self, sensor, location):
        '''
        Deletes the link between Location and Sensor.

        Returns Response object with satus code 200
        '''

        location.sensors.remove(sensor)
        db.session.commit()

        return Response(status=200)
