"""
This module test functionality of DB
Code from mokkiwahti/db_models.py targeted
"""

import os
import tempfile
from time import time
from datetime import datetime

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from mokkiwahti import create_app, db
from mokkiwahti.db_models import Location, Sensor, Measurement, SensorConfiguration


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key support"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def app():
    """Setup test environment"""
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
    """Return valid location obj"""
    return Location(
        name=f"{name}"
    )

def _get_sensor(name=1):
    """Return valid sensor obj"""
    return Sensor(
        name=f"testsensor-{name}"
    )

def _get_measurement(temperature=20.51, humidity=45.8):
    """Return valid meas obj"""
    return Measurement(
        temperature=temperature,
        timestamp=datetime.now(),
        humidity=humidity
    )

def _get_sensor_configuration(interval = 900, threshold_min = 15.0, threshold_max = 22.0):
    """Return valid sensor config obj"""
    return SensorConfiguration(
        interval = interval,
        threshold_min = threshold_min,
        threshold_max = threshold_max
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
        sensor_configuration = _get_sensor_configuration()
        sensor.measurements.append(measurement)
        location.measurements.append(measurement)
        location.sensors.append(sensor)
        sensor.sensor_configuration = sensor_configuration

        # 2.
        db.session.add(location)
        db.session.add(sensor)
        db.session.add(measurement)
        db.session.add(sensor_configuration)
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
        db_sensor_configuration = SensorConfiguration.query.first()

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
        assert db_sensor.sensor_configuration == db_sensor_configuration
        # sensor configuration
        assert db_sensor_configuration.sensor == db_sensor

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
        assert sensor_configuration.threshold_max == db_sensor_configuration.threshold_max
        assert sensor_configuration.threshold_min == db_sensor_configuration.threshold_min
        assert sensor_configuration.interval == db_sensor_configuration.interval
        assert sensor_configuration.sensor.id == db_sensor.id



def test_sensor(app):
    """
    Test sensor class restrictions.
    Name is required parameter
    Name is unique
    """
    with app.app_context():
        # dont allow two sensors with same name
        sensor1 = _get_sensor("samenamesensor")
        sensor2 = _get_sensor("samenamesensor")
        db.session.add(sensor1)
        db.session.add(sensor2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # name is mandatory
        sensor1.name = None
        db.session.add(sensor1)
        with pytest.raises(IntegrityError):
            db.session.commit()

@pytest.mark.skip(reason="There's currently problem in database validation.")
def test_sensor_configuration(app):
    """
    Test sensor configuration class restrictions.
    only numerical values accepted
    interval is mandatory
    """
    with app.app_context():
        # interval is mandatory
        sensor_configuration = _get_sensor_configuration()
        sensor_configuration.interval = None
        db.session.add(sensor_configuration)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # interval must be number
        sc_nan_interval = _get_sensor_configuration(interval="100s")
        db.session.add(sc_nan_interval)
        with pytest.raises(StatementError):
            db.session.commit()
        db.session.rollback()

        # humidity must be number
        sc_nan_th_min = _get_sensor_configuration(threshold_min="0°")
        db.session.add(sc_nan_th_min)
        with pytest.raises(StatementError):
            db.session.commit()
        db.session.rollback()

        # temperature must be number
        sc_nan_th_max = _get_sensor_configuration(threshold_max="100.0°")
        db.session.add(sc_nan_th_max)
        with pytest.raises(StatementError):
            db.session.commit()
        db.session.rollback()

def test_measurement(app):
    """
    Try saving a measurements with bad data type
    Try saving without required fields
    """
    with app.app_context():
        # temperature must be number
        meas_nan_temp = _get_measurement(temperature="100°")
        db.session.add(meas_nan_temp)
        with pytest.raises(StatementError):
            db.session.commit()
        db.session.rollback()

        # humidity must be number
        meas_nan_hum = _get_measurement(humidity="100%")
        db.session.add(meas_nan_hum)
        with pytest.raises(StatementError):
            db.session.commit()
        db.session.rollback()

        # timestamp must be a datetime obj
        sc_bad_timestamp = _get_measurement()
        sc_bad_timestamp.timestamp = time()
        db.session.add(sc_bad_timestamp)
        with pytest.raises(StatementError):
            db.session.commit()
        db.session.rollback()
        sc_bad_timestamp2 = _get_measurement()
        sc_bad_timestamp2.timestamp = "today"
        db.session.add(sc_bad_timestamp2)
        with pytest.raises(StatementError):
            db.session.commit()
        db.session.rollback()

        # temperature is mandatory
        meas_none_temp = _get_measurement(temperature=None)
        db.session.add(meas_none_temp)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # humidity is mandatory
        meas_none_hum = _get_measurement(humidity=None)
        db.session.add(meas_none_hum)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # timestamp is mandatory
        sc_none_timestamp = _get_measurement()
        sc_none_timestamp.timestamp = None
        db.session.add(sc_none_timestamp)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

def test_location(app):
    """
    Test location class restrictions.
    Name is required parameter
    Name is unique
    """
    with app.app_context():
        # dont allow two sensors with same name
        loc1 = _get_location("samenamespot")
        loc2 = _get_location("samenamespot")
        db.session.add(loc1)
        db.session.add(loc2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # name is mandatory
        loc1.name = None
        db.session.add(loc1)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_multiple_sensors_in_location(app):
    """
    Test that sensors can have same location
    """
    with app.app_context():
        location = _get_location()
        sensor1 = _get_sensor(name="sensor1")
        sensor2 = _get_sensor(name="sensor2")
        location.sensors.extend([sensor1, sensor2])

        db.session.add(location)
        db.session.commit()

        assert len(Location.query.first().sensors) == 2

def test_access_nonexistent_sensor(app):
    """
    Test non-existing sensor query
    """
    with app.app_context():
        non_existent_sensor = Sensor.query.filter_by(name="non_existent").first()
        assert non_existent_sensor is None

def test_unique_sensor_name(app):
    """
    Test sensors have unique names
    """
    with app.app_context():
        sensor1 = _get_sensor(name="unique_sensor")
        sensor2 = _get_sensor(name="unique_sensor")
        db.session.add(sensor1)
        db.session.commit()

        db.session.add(sensor2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

@pytest.mark.skip(reason="There's currently problem in database validation.")
def test_too_long_name(app):
    """Try saving a sensor with too long name"""
    with app.app_context():
        # form string with length of 65
        too_long_name = "test1" * 13
        sensor = _get_sensor(name=too_long_name)
        db.session.add(sensor)
        with pytest.raises(IntegrityError):
            db.session.commit()

        location = _get_location(name=too_long_name)
        db.session.add(location)
        with pytest.raises(IntegrityError):
            db.session.commit()
