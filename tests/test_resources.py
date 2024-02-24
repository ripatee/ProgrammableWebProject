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
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()

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