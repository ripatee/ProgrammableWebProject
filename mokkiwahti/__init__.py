import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Functionality borrowed from lovelace material

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    # Register ConverterClasses to be used in routing
    from . import api
    from mokkiwahti.utils import SensorConverter, MeasurementConverter, LocationConverter

    app.url_map.converters["sensor"] = SensorConverter
    app.url_map.converters["measurement"] = MeasurementConverter
    app.url_map.converters["location"] = LocationConverter

    # Register blueprint. Check api.py for more blueprint stuff
    app.register_blueprint(api.api_bp)

    from . import db_models
    app.cli.add_command(db_models.init_db_command)

    return app
