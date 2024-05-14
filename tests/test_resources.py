"""
This module test functionality of resources
Code from mokkiwahti/resources/*.py targeted
"""

import os
import json
import tempfile
from datetime import datetime

import pytest
from jsonschema import validate#, ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy import event

from mokkiwahti import create_app, db
from mokkiwahti.db_models import Location, Sensor, Measurement, SensorConfiguration


# Enable foreigen key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """setup"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def _get_location(name="testipaikka"):
    """returns valid location obj for testing"""
    return Location(
        name=f"{name}"
    )

def _get_sensor(name=1):
    """returns valid sensor obj for testing"""
    return Sensor(
        name=f"testsensor-{name}"
    )

def _get_measurement(temperature=20.51, humidity=45.8):
    """returns valid meas obj for testing"""
    return Measurement(
        temperature=temperature,
        timestamp=datetime.now(),
        humidity=humidity
    )

def _get_sensor_configuration(interval = 900, threshold_min = 15.0, threshold_max = 22.0):
    """returns valid sensor config obj for testing"""
    return SensorConfiguration(
        interval = interval,
        threshold_min = threshold_min,
        threshold_max = threshold_max
    )

def _populate_db():
    """populates db for testing purposes"""
    for i in range(1, 4):
        # create 3 instances per class
        sensor = Sensor(name=f"testsensor-{i}")
        location = Location(name=f"testlocation-{i}")
        sc = SensorConfiguration(
            interval = i,
            threshold_min = i,
            threshold_max = i
        )
        meas = Measurement(
            temperature = i,
            humidity = i,
            timestamp = datetime.now()
        )
        # add relationships
        sensor.sensor_configuration = sc
        location.sensors.append(sensor)
        location.measurements.append(meas)
        sensor.measurements.append(meas)
        # add to DB
        db.session.add(sensor)
        db.session.add(location)
        db.session.add(sc)
        db.session.add(meas)

    db.session.commit()

def _check_db():
    """
    Prints contents of DB
    Debug purposes
    """
    print("location count: ", Location.query.count())
    print("sensor count: ", Sensor.query.count())
    print("sensor configuration count: ", SensorConfiguration.query.count())
    print("measurement count: ", Measurement.query.count())

@pytest.fixture
def client():
    """test client setup"""
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()
        #_check_db()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)

class TestLocationResource():
    """Tests for Location resource"""
    RESOURCE_URL = "/api/locations/"

    def test_get(self, client):
        """test get method functionality"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        for loc in body:
            validate(loc, Location.get_schema())

    def test_post(self, client):
        """test post method functionality"""
        data = {"name": "testlocation-100"}
        resp = client.post(self.RESOURCE_URL, json=data)
        assert resp.status_code == 201
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert len(body) == 4
        new_found = False #temp to check that new loc is added
        for loc in body:
            validate(loc, Location.get_schema())
            if loc["name"] == "testlocation-100":
                new_found = True
        assert new_found

    def test_post_dub(self, client):
        """test duplicate post method functionality"""
        data = {"name": "testlocation-1"}
        resp = client.post(self.RESOURCE_URL, json=data)
        assert resp.status_code == 409
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(body) == 3

    def test_post_new_location_bad_request(self, client):
        """test post method with invalid data"""
        invalid_location_data = {"invalid_field": "value"}
        response = client.post(self.RESOURCE_URL, json=invalid_location_data)
        assert response.status_code == 400


    def test_put_modify_location(self, client):
        """test put method with valid data"""
        client.post(self.RESOURCE_URL, json={"name": "Initial Location Name"})

        response = client.get(self.RESOURCE_URL)
        locations = json.loads(response.data)
        location_name = locations[0]['name']

        updated_location_data = {"name": "Updated Location Name"}
        modify_response = client.put(f'/api/locations/{location_name}/',
                                     json=updated_location_data)  # Use the identifier in the URL
        assert modify_response.status_code == 200

    def test_post_w_bad_data(self, client):
        """test post method with bad data"""
        data = {"extrafield": "thisisnotsupposedtobehere"}
        resp = client.post(self.RESOURCE_URL, json=data)
        assert resp.status_code == 400
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert len(body) == 3
        new_found = False #temp to check that new loc is added
        for loc in body:
            validate(loc, Location.get_schema())
            if loc["name"] == "thisisnotsupposedtobehere":
                new_found = True
        assert not new_found

class TestLinkerResource():
    """Tests for Linker resource"""
    RESOURCE_URL = "/api/locations/testlocation-1/link/sensors/testsensor-1/"

    def test_put(self, client):
        """test put method functionality"""
        # add two sensors in same location
        resp = client.put(self.RESOURCE_URL)
        assert resp.status_code == 200
        resp = client.put("/api/locations/testlocation-1/link/sensors/testsensor-2/")
        assert resp.status_code == 200

        # get sensor by name and check loc
        get_sensors_resp = client.get("/api/sensors/testsensor-1/")
        body = json.loads(get_sensors_resp.data)
        validate(body, Sensor.get_schema())
        assert body["location"]["name"] == "testlocation-1"

        get_sensors_resp2 = client.get("/api/sensors/testsensor-2/")
        body2 = json.loads(get_sensors_resp2.data)
        validate(body, Sensor.get_schema())
        assert body2["location"]["name"] == "testlocation-1"

        # get loc by name and check both sensors
        get_loc_resp = client.get("/api/locations/testlocation-1/")
        body = json.loads(get_loc_resp.data)
        validate(body, Location.get_schema())
        for i, sensor in enumerate(body["sensors"], start=1):
            assert "testsensor-" + str(i) == sensor["name"]

    def test_put_wo_sensor(self, client):
        """test put method with missing sensor"""
        resp = client.put("/api/locations/testlocation-1/link/sensors/testsensor-100/")
        assert resp.status_code == 404

    def test_put_wo_location(self, client):
        """test put method with missing location"""
        resp = client.put("/api/locations/testlocation-100/link/sensors/testsensor-1/")
        assert resp.status_code == 404

    # test deleting
    def test_delete(self, client):
        """test delete method functionality"""
        # get data before
        get_sensor_before = client.get("/api/sensors/testsensor-1/")
        get_loc_before = client.get("/api/locations/testlocation-1/")
        body_s_1 = json.loads(get_sensor_before.data)
        body_l_1 = json.loads(get_loc_before.data)
        # delete relationship
        delete_resp = client.delete("/api/locations/testlocation-1/link/sensors/testsensor-1/")
        assert delete_resp.status_code == 200
        # get data after
        get_sensor_after = client.get("/api/sensors/testsensor-1/")
        get_loc_after = client.get("/api/locations/testlocation-1/")
        body_s_2 = json.loads(get_sensor_after.data)
        body_l_2 = json.loads(get_loc_after.data)
        # check that object is not broken
        validate(body_s_2, Sensor.get_schema())
        validate(body_l_2, Location.get_schema())
        # check that relationship existed
        assert body_s_1["location"]["name"] == "testlocation-1"
        assert len(body_l_1["sensors"]) == 1
        assert "testsensor-1" == body_l_1["sensors"][0]["name"]
        # check that relationship no more exists
        assert body_s_2["location"] is None
        assert len(body_l_2["sensors"]) == 0

class TestSensorResource():
    """Tests for sensor resource"""
    RESOURCE_URL = "/api/sensors/"

    def test_get(self, client):
        """test get method functionality"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        for sensor in body:
            validate(sensor, Sensor.get_schema())

    def test_post(self, client):
        """test post method functionality"""
        data = {"name": "testsensor-100"}
        sc = SensorConfiguration(
            interval = 900,
            threshold_min = 15,
            threshold_max = 25
        )
        data["sensor_configuration"] = sc.serialize()
        resp = client.post(self.RESOURCE_URL, json=data)
        assert resp.status_code == 201
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert resp.status_code == 200
        new_found = False #temp to check that new sensor is added
        assert len(body) == 4
        for sensor in body:
            validate(sensor, Location.get_schema())
            if sensor["name"] == "testsensor-100":
                new_found = True
        assert new_found

    def test_post_dub(self, client):
        """test duplicate post method functionality"""
        data = {"name": "testsensor-1"}
        sc = SensorConfiguration(
            interval = 900,
            threshold_min = 15,
            threshold_max = 25
        )
        data["sensor_configuration"] = sc.serialize()
        resp = client.post(self.RESOURCE_URL, json=data)
        assert resp.status_code == 409
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(body) == 3

    def test_post_w_bad_data(self, client):
        """test post method with bad data"""
        data = {"name": "testsensor-101"}
        data["extrafield"] = "thisisnotsupposedtobehere"
        resp = client.post(self.RESOURCE_URL, json=data)
        assert resp.status_code == 400
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert resp.status_code == 200
        new_found = False #temp to check that new sensor is added
        assert len(body) == 3
        for sensor in body:
            validate(sensor, Location.get_schema())
            if sensor["name"] == "testsensor-101":
                new_found = True
        assert not new_found

    def test_non_json_post(self, client):
        """test post method with empty json field"""
        meas_test_obj =  _get_sensor()
        resp = client.post(self.RESOURCE_URL, data=meas_test_obj.serialize())
        assert resp.status_code == 415

    def test_bad_json_post(self, client):
        """test post method with missing required field"""
        test_obj =  Sensor(
            name = "test_sensor",
            sensor_configuration = _get_sensor_configuration()
        )
        data = test_obj.serialize()
        del data["name"]
        resp = client.post(self.RESOURCE_URL, json=data)
        assert resp.status_code == 400

class TestMeasurementsResource():
    """Tests for measurements resource"""

    SENSOR_RESOURCE_URL = "/api/sensors/testsensor-1/measurements/"
    LOCATION_RESOURCE_URL = "/api/locations/testlocation-1/measurements/"

    def test_get_by_sensor(self, client):
        """test get method functionality"""
        resp = client.get(self.SENSOR_RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 1
        validate(body[0], Measurement.get_schema())

    def test_get_by_location(self, client):
        """test get method functionality"""
        resp = client.get(self.LOCATION_RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 1
        validate(body[0], Measurement.get_schema())

    def test_post(self, client):
        """test post method functionality"""
        meas_test_obj =  Measurement(
            temperature = 22.2,
            humidity = 55.2,
            timestamp = datetime.now()
        )
        resp = client.post(self.SENSOR_RESOURCE_URL, json=meas_test_obj.serialize())
        assert resp.status_code == 201
        resp = client.get(self.SENSOR_RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 2
        for meas in body:
            validate(meas, Measurement.get_schema())

    def test_non_json_post(self, client):
        """test post method with empty json field"""
        meas_test_obj =  Measurement(
            temperature = 22.2,
            humidity = 55.2,
            timestamp = datetime.now()
        )
        resp = client.post(self.SENSOR_RESOURCE_URL, data=meas_test_obj.serialize())
        assert resp.status_code == 415

    def test_bad_json_post(self, client):
        """test post method with missing required field"""
        meas_test_obj =  Measurement(
            temperature = 22.2,
            humidity = 55.2,
            timestamp = datetime.now()
        )
        data = meas_test_obj.serialize()
        del data["timestamp"]
        resp = client.post(self.SENSOR_RESOURCE_URL, json=data)
        assert resp.status_code == 400

    def test_post_w_bad_data(self, client):
        """test post method using bad data"""
        meas_test_obj =  Measurement(
            temperature = 23.2,
            humidity = 53.2,
            timestamp = datetime.now()
        )
        meas_test_obj_serialized = meas_test_obj.serialize()
        del meas_test_obj_serialized["temperature"]
        meas_test_obj_serialized["extrafield"] = "thisisnotsupposedtobehere"
        #print("\n\nobject here\n", meas_test_obj_serialized, "\n\n") # debug print
        resp = client.post(self.SENSOR_RESOURCE_URL, json=meas_test_obj_serialized)
        assert resp.status_code == 400
        resp = client.get(self.SENSOR_RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        #print("\n\nsaved here\n", body, "\n\n") # debug print
        assert len(body) == 1
        for meas in body:
            validate(meas, Measurement.get_schema())

class TestSensorItem():
    """Tests for sensor object"""
    RESOURCE_URL = "/api/sensors/testsensor-1/"

    def test_get_by_sensor(self, client):
        """test get method functionality with given sensor"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        validate(body, Sensor.get_schema())

    def test_put(self, client):
        """test post method functionality with valid data"""
        # get sensor data
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        sensor = resp.json
        # modify data and send it back
        sc = SensorConfiguration(
            interval = 4,
            threshold_min = 4,
            threshold_max = 4
        ).serialize()
        sensor["sensor_configuration"] = sc
        resp2 = client.put(self.RESOURCE_URL, json=sensor)
        assert resp2.status_code == 200
        resp3 = client.get(self.RESOURCE_URL)
        assert resp3.status_code == 200
        assert resp3.json["sensor_configuration"]["interval"] == 4

    def test_put_w_bad_request(self, client):
        """test put method functionality with bad data"""
        # get sensor data
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        sensor = resp.json
        del sensor["sensor_configuration"]
        resp2 = client.put(self.RESOURCE_URL, json=sensor)
        assert resp2.status_code == 400

    def test_delete(self, client):
        """test delete method functionality"""
        # test first sensor exists
        resp_before = client.get(self.RESOURCE_URL)
        assert resp_before.status_code == 200

        # now delete sensor
        resp_deletion = client.delete(self.RESOURCE_URL)
        assert resp_deletion.status_code == 200

        # test is the sensor deleted
        resp_after = client.get(self.RESOURCE_URL)
        assert resp_after.status_code == 404



class TestLocationItem():
    """Tests for location object"""
    RESOURCE_URL = "/api/locations/testlocation-1/"

    def test_get_by_location(self, client):
        """test get method functionality"""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        validate(body, Location.get_schema())

    def test_put_w_bad_request(self, client):
        """test put method functionality with bad data"""
        # get sensor data
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        location = resp.json
        del location["name"]
        resp2 = client.put(self.RESOURCE_URL, json=location)
        assert resp2.status_code == 400

    def test_delete(self, client):
        """test delete method functionality"""
        # test first location exists
        resp_before = client.get(self.RESOURCE_URL)
        assert resp_before.status_code == 200

        # now delete location
        resp_deletion = client.delete(self.RESOURCE_URL)
        assert resp_deletion.status_code == 200

        # test is the location deleted
        resp_after = client.get(self.RESOURCE_URL)
        assert resp_after.status_code == 404


class TestMeasurementItem():
    """Tests for measurement object"""
    RESOURCE_URL = "/api/sensors/testsensor-1/measurements/"

    def test_put(self, client):
        """test put method functionality"""
        meas_test_obj =  Measurement(
            temperature = 22.2,
            humidity = 55.2,
            timestamp = datetime.now()
        )
        meas_test_obj2 =  Measurement(
            temperature = 12.3,
            humidity = 45.6,
            timestamp = datetime.now()
        )
        resp = client.post(self.RESOURCE_URL, json=meas_test_obj.serialize())
        meas_url = resp.headers["Location"]
        assert resp.status_code == 201
        resp2 = client.put(meas_url, json=meas_test_obj2.serialize())
        assert resp2.status_code == 200

    def test_delete(self, client):
        """test delete method functionality"""
        # create and get meas resource url
        meas_test_obj =  Measurement(
            temperature = 22.2,
            humidity = 55.2,
            timestamp = datetime.now()
        )
        resp = client.post(self.RESOURCE_URL, json=meas_test_obj.serialize())
        meas_url = resp.headers["Location"]

        # make sure new meas added
        resp_after = client.get(self.RESOURCE_URL)
        assert len(resp_after.json) == 2

        # delete measurement
        resp_deletion = client.delete(meas_url)
        assert resp_deletion.status_code == 200

        # test is the measurement deleted
        resp_after = client.get(self.RESOURCE_URL)
        assert len(resp_after.json) == 1
