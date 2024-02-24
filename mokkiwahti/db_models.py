from mokkiwahti import db

# ORM classes and related functions live here

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    measurement_id = db.Column(db.Integer, db.ForeignKey("measurement.id", ondelete="SET NULL"))
    
    sensor = db.relationship("Sensor", back_populates="location")
    measurement = db.relationship("Measurement", back_populates="location")


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True) # serial code etc?
    location_id = (db.Integer, db.ForeignKey("location.id", ondelete="SET NULL"))

    location = db.relationship("Location", back_populates="sensor")
    measurement = db.relationship("Measurement", back_populates="sensor")
    sensor_configuration = db.relationship("SensorConfiguration", back_populates="sensor")

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    location_id = (db.Integer, db.ForeignKey("location.id", ondelete="SET NULL"))

    location = db.relationship("Location", back_populates="measurement")
    sensor = db.relationship("Sensor", back_populates="measurement")

class SensorConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    interval = db.Column(db.Integer, nullable=False)
    treshold_min = db.Column(db.Float)
    treshold_max = db.Column(db.Float)

    sensor = db.relationship("Sensor", back_populates="sensor_configuration")

# ADD methods

# add a location to the database
def add_location(name):
    location = Location(location_name=name)
    db.session.add(location)
    db.session.commit()

# add a sensor to the database
def add_sensor(name, location_id):
    sensor = Sensor(device_name=name, location_id=location_id)
    db.session.add(sensor)
    db.session.commit()

# add a measurement to the database
def add_measurement(sensor_id, timestamp, temperature, humidity):
    # make sure sensor exists and get its location
    sensor = db.session.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if sensor:
        measurement = Measurement(  sensor_id=sensor_id,
                                    timestamp=timestamp,
                                    temperature=temperature,
                                    humidity=humidity,
                                    location_id=sensor.location_id
                                )
        db.session.add(measurement)
        db.session.commit()
    else:
        # TODO Add proper ERR handler
        print(f"ERROR sensor with ID {sensor_id} not found. Action denied.")

#add a config to sensor
def add_config(sensor_id, threshold_max=None, threshold_min=None):
    config = Sensor(sensor_id=sensor_id, threshold_max=threshold_max, threshold_min=threshold_min)
    db.session.add(config)
    db.session.commit()

# GET methods

# method to query all measurements
def get_all_measurements():
    return db.session.query(Measurement).all()

# method to query measurements for a specific sensor
def get_measurements_for_sensor(sensor_id):
    return db.session.query(Measurement).filter(Measurement.sensor_id == sensor_id).all()

# method to query measurements for a specific location
def get_measurements_for_location(location_id):
    return db.session.query(Measurement).filter(Measurement.location_id == location_id).all()

# method to query all sensors
def get_all_sensors():
    return db.session.query(Sensor).all()

# method to query all locations
def get_all_locations():
    return db.session.query(Location).all()

# method to query all configurations
def get_all_configurations():
    return db.session.query(SensorConfiguration).all()

# method to query configurations by sensor_id
def get_configuration_by_sensor_id(sensor_id):
    return db.session.query(SensorConfiguration).filter(SensorConfiguration.sensor_id == sensor_id).all()
