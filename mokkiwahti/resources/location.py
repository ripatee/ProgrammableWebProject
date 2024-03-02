'''
API resources related to Locations
'''

import json

from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

from mokkiwahti.db_models import Location
from mokkiwahti import db

class LocationCollection(Resource):
    '''
    LocationCollection resource. Supports GET and POST methods
    '''

    def get(self):
        '''
        Returns all locations as a HTTP Response that contains JSON object
        '''

        locations = []
        for location in Location.query.all():
            locations.append(location.serialize())

        return Response(json.dumps(locations), 200, mimetype='application/json')

    def post(self):
        '''
        Add new location to database

        Checks that the input is JSON and validates it against the schema
        Deserializes the Location object from JSON
        Adds location to database
        Sends response containing location to the newly added location
        '''

        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Location.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        try:
            location = Location()
            location.deserialize(request.json)

            db.session.add(location)
            db.session.commit()
        except IntegrityError as e:
            raise Conflict(
                description=f"Location with name: {location.name} already found"
            ) from e
        return Response(status=201, headers={
            "Location": url_for("api.locationitem", location=location)
        })

class LocationItem(Resource):
    '''
    Location item resource. Supports GET, PUT and DELETE methods.
    '''

    def get(self, location):
        '''
        Returns a Response containing a specific location item
        '''

        return Response(json.dumps(location.serialize()), 200, mimetype='application/json')

    def put(self, location):
        '''
        Modifies an existing location resourse

        Checks that the input is a JSON and validates it agains the schema
        Adds it to the database and returns a Response object with status code 201
        '''

        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Location.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        location.deserialize(request.json)
        db.session.commit()

        return Response(status=200, headers={
            "Location": "Location TBA"
        })


    def delete(self, location):
        '''
        Deletes a specific location item from the database

        Returns a Response object with status code 200
        '''

        db.session.delete(location)
        db.session.commit()
        return Response(
            status=200
        )
