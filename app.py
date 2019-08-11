import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br>"
        f'/api/v1.0/start_date/end_date'
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return one year of precipitation data"""   
    results = session.query(Measurement.date, func.sum(Measurement.prcp))\
        .filter(Measurement.date > '2016-08-23').group_by(Measurement.date)\
        .order_by(Measurement.date).all()
    
    precipitation_data = []
    for date, prcp in results:      
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['prcp'] = prcp
        precipitation_data.append(precip_dict)
    
    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of weather stations"""
    # Query all stations
    results = session.query(Station.station).all()
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def temperature_observations():
    """Return Temperature Observations for the Previous Year"""
    
    results = session.query(Measurement.date, Measurement.tobs)\
            .filter(Measurement.date > '2016-08-23').order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of temperature observations
    temp_obs = []
    for date, temp in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temp"] = temp
        temp_obs.append(temp_dict)
    
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return temperature data from a given start date"""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return temperature data between a start date and end date"""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)