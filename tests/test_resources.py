import os
import pytest
import tempfile
from datetime import datetime

from mokkiwahti import create_app, db

from mokkiwahti.db_models import Location, Sensor, Measurement, SensorConfiguration
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

def _get_sensor_configuration(interval = 900, treshold_min = 15.0, treshold_max = 22.0):
    return SensorConfiguration(
        interval = interval,
        treshold_min = treshold_min,
        treshold_max = treshold_max
    )

def _populate_db():
    for i in range(1, 4):
        s = Sensor(name="testsensor-{}".format(i))
        l = Location(name="testlocation-{}".format(i))
        sc = SensorConfiguration(
            interval = i,
            treshold_min = i,
            treshold_max = i
        )
        m = Measurement(
            temperature = i,
            humidity = i,
            timestamp = datetime.now()
        )
        db.session.add(s)
        db.session.add(l)
        db.session.add(sc)
        db.session.add(m)

    db.session.commit()

def _check_db():
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

class TestLinkerResource(object):
    
    RESOURCE_URL = "/api/locations/testlocation-1/link/sensors/testsensor-1/"

    # no get method in resource
    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 405
    
    # no post method in resource
    def test_post(self, client):
        sensor_data = {"name": "testsensor-100"}
        resp = client.post(self.RESOURCE_URL, json=sensor_data)
        assert resp.status_code == 405

    # test put method
    def test_put(self, client):
        resp = client.put(self.RESOURCE_URL)
        assert resp.status_code == 200

    # test put method with missing sensor
    def test_put_wo_sensor(self, client):
        resp = client.put("/api/locations/testlocation-1/link/sensors/testsensor-100/")
        assert resp.status_code == 404

    # test put method with missing location
    def test_put_wo_location(self, client):
        resp = client.put("/api/locations/testlocation-100/link/sensors/testsensor-1/")
        assert resp.status_code == 404