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


@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()
        
    yield app
    
    os.close(db_fd)
    os.unlink(db_fname)

def _get_location(name="testipaikka"):
    return Location(
        name="{}".format(name),
    )

def _get_sensor(number=1):
    return Sensor(
        name="testsensor-{}".format(number),
    )
    
def _get_measurement():
    return Measurement(
        temperature=20.51,
        timestamp=datetime.now(),
        humidity=45.8
    )

def _get_sensorconfiguration(number=1):
    return SensorConfiguration(
        interval = 900,
        treshold_min = 15.0,
        treshold_max = 22.0
    )

def test_create_instances(app):
    """
    Test that DB is saving values and relations as intented
    given valid input
    1. create valid instances of all classes
    2. save them to db
    3. check all of them exist
    4. check all relationships (both sides)
    5. check that saved values match to given ones
    """
    
    with app.app_context():
        # 1.
        location = _get_location()
        sensor = _get_sensor()
        measurement = _get_measurement()
        sensorconfiguration = _get_sensorconfiguration()
        sensor.measurements.append(measurement)
        location.measurements.append(measurement)
        location.sensors.append(sensor)
        sensor.sensor_configuration = sensorconfiguration

        # 2.
        db.session.add(location)
        db.session.add(sensor)
        db.session.add(measurement)
        db.session.add(sensorconfiguration)
        db.session.commit()

        # 3.
        assert Location.query.count() == 1
        assert Sensor.query.count() == 1
        assert Measurement.query.count() == 1
        assert SensorConfiguration.query.count() == 1

        # get items saved in db
        db_sensor = Sensor.query.first()
        db_measurement = Measurement.query.first()
        db_location = Location.query.first()
        db_sensorconfiguration = SensorConfiguration.query.first()

        # 4.
        # measurement
        assert db_measurement.sensor == db_sensor
        assert db_measurement.location == db_location
        # location
        assert db_sensor in db_location.sensors
        assert db_measurement in db_location.measurements
        # sensor
        assert db_sensor.location == db_location
        assert db_measurement in db_sensor.measurements
        assert db_sensor.sensor_configuration == db_sensorconfiguration
        # sensor configuration
        assert db_sensorconfiguration.sensor == db_sensor

        # 5.
        # sensor
        assert sensor.name == db_sensor.name
        assert sensor.location_id == db_location.id
        # measurement
        assert measurement.temperature == db_measurement.temperature
        assert measurement.humidity == db_measurement.humidity
        assert measurement.timestamp == db_measurement.timestamp
        assert measurement.sensor_id == db_sensor.id
        assert measurement.location_id == location.id
        # location
        assert location.name == db_location.name
        # sensor configuration
        assert sensorconfiguration.treshold_max == db_sensorconfiguration.treshold_max
        assert sensorconfiguration.treshold_min == db_sensorconfiguration.treshold_min
        assert sensorconfiguration.interval == db_sensorconfiguration.interval
        assert sensorconfiguration.sensor_id == db_sensor.id



def test_create_sensor(app):
    with app.app_context():
        sensor = Sensor(
            name = "test-sensor-1"
        )
        db.session.add(sensor)
        db.session.commit()
        assert Sensor.query.count() == 1
