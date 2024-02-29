import json
from flask import request, Response, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from mokkiwahti.db_models import Location
from mokkiwahti import db
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

class LocationCollection(Resource):

    def get(self): # get all locations
        locations = []
        for location in Location.query.all():
            locations.append(location.serialize())

        return Response(json.dumps(locations), 200, mimetype='application/json')
        

    def post(self): # add new location
        if not request.json:     
            raise UnsupportedMediaType
        
        try:
            validate(request.json, Location.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        
        try:
            location = Location()
            location.deserialize(request.json)

            db.session.add(location)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                description=f"Location with name: {location.name} already found"
            )
        return Response(status=201, headers={
            "Location": url_for("api.locationitem", location=location)
        })

class LocationItem(Resource):

    def get(self, location): # get specific measurement
        return Response(json.dumps(location.serialize()), 200, mimetype='application/json')

    def put(self, location): # modify specific measurement
        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Location.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        
        location.deserialize(request.json)
        db.session.commit()

        return Response(status=200, headers={
            "Location": "Location TBA"
        })
    
    
    def delete(self, location): # delete specific measurement
        # error handing needed?
        db.session.delete(location)
        db.session.commit()
        return Response(
            status=200
        )
    
    