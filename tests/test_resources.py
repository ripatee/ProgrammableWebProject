import os
import json
import pytest
import tempfile
from datetime import datetime

from mokkiwahti import create_app, db

from mokkiwahti.db_models import Location, Sensor, Measurement, SensorConfiguration
from jsonschema import validate, ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy import event

# Enable foreigen key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def _get_location(name="testipaikka"):
    return Location(
        name="{}".format(name),
    )

def _get_sensor(name=1):
    return Sensor(
        name="testsensor-{}".format(name),
    )

def _get_measurement(temperature=20.51, humidity=45.8):
    return Measurement(
        temperature=temperature,
        timestamp=datetime.now(),
        humidity=humidity
    )

def _get_sensor_configuration(interval = 900, threshold_min = 15.0, threshold_max = 22.0):
    return SensorConfiguration(
        interval = interval,
        threshold_min = threshold_min,
        threshold_max = threshold_max
    )

def _populate_db():
    for i in range(1, 4):
        # create 3 instances per class
        s = Sensor(name="testsensor-{}".format(i))
        l = Location(name="testlocation-{}".format(i))
        sc = SensorConfiguration(
            interval = i,
            threshold_min = i,
            threshold_max = i
        )
        m = Measurement(
            temperature = i,
            humidity = i,
            timestamp = datetime.now()
        )
        # add relationships
        s.sensor_configuration = sc
        l.sensors.append(s)
        l.measurements.append(m)
        s.measurements.append(m)
        # add to DB
        db.session.add(s)
        db.session.add(l)
        db.session.add(sc)
        db.session.add(m)

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

def test_hello_world(client):
    # Simple test just to make sure that the tests run
    pass

class TestLocationResource(object):

    RESOURCE_URL = "/api/locations/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        for loc in body:
            validate(loc, Location.get_schema())

    def test_post(self, client):
        data = {"name": "testlocation-100"}
        resp = client.post(self.RESOURCE_URL, json=data)
        assert resp.status_code == 201
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        new_found = False #temp to check that new loc is added
        for loc in body:
            validate(loc, Location.get_schema())
            if loc["name"] == "testlocation-100":
                new_found = True
        assert new_found

class TestLinkerResource(object):

    RESOURCE_URL = "/api/locations/testlocation-1/link/sensors/testsensor-1/"

    # test put method
    def test_put(self, client):
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

    # test put method with missing sensor
    def test_put_wo_sensor(self, client):
        resp = client.put("/api/locations/testlocation-1/link/sensors/testsensor-100/")
        assert resp.status_code == 404

    # test put method with missing location
    def test_put_wo_location(self, client):
        resp = client.put("/api/locations/testlocation-100/link/sensors/testsensor-1/")
        assert resp.status_code == 404

class TestSensorResource(object):

    RESOURCE_URL = "/api/sensors/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        for sensor in body:
            validate(sensor, Sensor.get_schema())

    def test_post(self, client):
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
        for sensor in body:
            validate(sensor, Location.get_schema())
            if sensor["name"] == "testsensor-100":
                new_found = True
        assert new_found
        
@pytest.mark.skip(reason="Not implemented")
class TestGetAllMeasurementResource(object):
    
    RESOURCE_URL = "/api/measurements/"
    
    pytest.mark.skip(reason="Not implemented")
    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        for meas in body:
            validate(meas, Measurement.get_schema())

class TestMeasurementsResource(object):
    
    SENSOR_RESOURCE_URL = "/api/sensors/testsensor-1/measurements/"
    LOCATION_RESOURCE_URL = "/api/locations/testlocation-1/measurements/"

    def test_get_by_sensor(self, client):
        resp = client.get(self.SENSOR_RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 1
        validate(body[0], Measurement.get_schema())

    def test_get_by_location(self, client):
        resp = client.get(self.LOCATION_RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 1
        validate(body[0], Measurement.get_schema())

    def test_post(self, client):
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
