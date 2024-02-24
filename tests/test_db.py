import os
import pytest
import tempfile

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

def test_create_sensor(app):
    with app.app_context():
        sensor = Sensor(
            name="test-sensor-1",
        )
        db.session.add(sensor)
        db.session.commit()
        assert Sensor.query.count() == 1
