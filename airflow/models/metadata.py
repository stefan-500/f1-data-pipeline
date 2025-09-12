from models.base import Base
from sqlalchemy import Column, Integer, String, Date, Time, Float, Interval, CHAR, ForeignKey
from sqlalchemy.orm import relationship

class Status(Base):
    __tablename__ = "dim_status"

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20), nullable=True)

    race_results = relationship("RaceResult", back_populates="status")

class _Time(Base):
    __tablename__ = "dim_time"

    time_id = Column(Integer, primary_key=True, autoincrement=False)
    time_year = Column(String(4), nullable=True)
    time_date = Column(Date, nullable=True)
    time_of_day = Column(Time, nullable=True)

    race = relationship("Race", back_populates="time")

class QualificationDate(Base):
    __tablename__ = "dim_quali_dates"

    quali_date_id = Column(Integer, primary_key=True, autoincrement=False)
    race_id = Column(Integer, ForeignKey('dim_races.race_id'))
    quali_date = Column(Date, nullable=True)

    race = relationship("Race", back_populates="qualifying")

class Circuit(Base):
    __tablename__ = "dim_circuits"

    circuit_id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_ref = Column(String(20), nullable=True)
    circuit_name = Column(String(50), nullable=True)
    url = Column(String(100), nullable=True)
    circuit_location = Column(String(45), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    altitude = Column(Integer, nullable=True)
    country = Column(String(30), nullable=True)

    race = relationship("Race", back_populates="circuit")

class Race(Base):
    __tablename__ = "dim_races"

    race_id = Column(Integer, primary_key=True, autoincrement=True)
    time_id = Column(Integer, ForeignKey('dim_time.time_id'))
    circuit_id = Column(Integer, ForeignKey('dim_circuits.circuit_id'))
    race_name = Column(String(80), nullable=True)
    url = Column(String(100), nullable=True)
    round = Column(Integer, nullable=True)

    circuit = relationship("Circuit", back_populates="race")
    time = relationship("_Time", back_populates="race")
    qualifying = relationship("QualificationDate", back_populates="race")
    driver_standings = relationship("DriverStanding", back_populates="race")
    constructor_standings = relationship("ConstructorStanding", back_populates="race")
    lap_times = relationship("LapTime", back_populates="race")
    pit_stops = relationship("PitStop", back_populates="race")
    race_results = relationship("RaceResult", back_populates="race")

class Constructor(Base):
    __tablename__ = "dim_constructors"

    constructor_id = Column(Integer, primary_key=True, autoincrement=True)
    const_ref = Column(String(50), nullable=True)
    const_name = Column(String(30), nullable=True)
    nationality = Column(String(30), nullable=True)
    url = Column(String(100), nullable=True)

    driver_standing = relationship("DriverStanding", back_populates="constructors")
    # A constructor can be located in many const standings 
    # (new const standing list after every race)
    constructor_standings = relationship("ConstructorStanding", back_populates="constructor")
    race_results = relationship("RaceResult", back_populates="constructor")

class Driver(Base):
    __tablename__ = "dim_drivers"

    driver_id = Column(Integer, primary_key=True, autoincrement=True)
    driver_ref = Column(String(50), nullable=True)
    forename = Column(String(30), nullable=True)
    surname = Column(String(30), nullable=True)
    dob = Column(Date, nullable=True)
    nationality = Column(String(30), nullable=True)
    url = Column(String(100), nullable=True)
    driver_num = Column(Integer, nullable=True)
    code = Column(CHAR(3), nullable=True)

    driver_standings = relationship("DriverStanding", back_populates="driver")
    lap_times = relationship("LapTime", back_populates="driver")
    pit_stops = relationship("PitStop", back_populates="driver")
    race_results = relationship("RaceResult", back_populates="driver")

class DriverStanding(Base):
    __tablename__ = "fact_driver_standings"

    driv_stand_id = Column(Integer, primary_key=True, autoincrement=True)
    driver_id = Column(Integer, ForeignKey('dim_drivers.driver_id'))
    constructor_id = Column(Integer, ForeignKey('dim_constructors.constructor_id'))
    race_id = Column(Integer, ForeignKey('dim_races.race_id'))
    points = Column(Float(precision=1), nullable=True)
    driv_position = Column(Integer, nullable=True)
    position_text = Column(String(2), nullable=True)
    wins = Column(Integer, nullable=True)

    driver = relationship("Driver", back_populates="driver_standings")
    constructors = relationship("Constructor", back_populates="driver_standing")
    race = relationship("Race", back_populates="driver_standings")

class ConstructorStanding(Base):
    __tablename__ = "fact_constructor_standings"

    const_stand_id = Column(Integer, primary_key=True, autoincrement=True)
    constructor_id = Column(Integer, ForeignKey('dim_constructors.constructor_id'))
    race_id = Column(Integer, ForeignKey('dim_races.race_id'))
    points = Column(Float(precision=1), nullable=True)
    const_position = Column(Integer, nullable=True)
    position_text = Column(String(2), nullable=True)
    wins = Column(Integer, nullable=True)

    constructor = relationship("Constructor", back_populates="constructor_standings")
    race = relationship("Race", back_populates="constructor_standings")

class LapTime(Base):
    __tablename__ = "fact_lap_times"

    lt_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('dim_races.race_id'))
    driver_id = Column(Integer, ForeignKey('dim_drivers.driver_id'))
    lap = Column(Integer, nullable=True)
    lt_position = Column(Integer, nullable=True)
    passing_time = Column(Interval, nullable=True)
    milliseconds = Column(Integer, nullable=True)

    race = relationship("Race", back_populates="lap_times")
    driver = relationship("Driver", back_populates="lap_times")

class PitStop(Base):
    __tablename__ = "fact_pit_stops"

    ps_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('dim_races.race_id'))
    driver_id = Column(Integer, ForeignKey('dim_drivers.driver_id'))
    stop = Column(Integer, nullable=True)
    lap = Column(Integer, nullable=True)
    ps_time = Column(Time, nullable=True) # start time
    duration = Column(Interval, nullable=True)
    milliseconds = Column(Integer, nullable=True)

    race = relationship("Race", back_populates="pit_stops")
    driver = relationship("Driver", back_populates="pit_stops")

class RaceResult(Base):
    __tablename__ = "fact_race_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('dim_races.race_id'))
    driver_id = Column(Integer, ForeignKey('dim_drivers.driver_id'))
    status_id = Column(Integer, ForeignKey('dim_status.status_id'))
    constructor_id = Column(Integer, ForeignKey('dim_constructors.constructor_id'))
    laps = Column(Integer, nullable=True)
    passing_time = Column(Interval, nullable=True)
    car_number = Column(Integer, nullable=True)
    grid = Column(Integer, nullable=True)
    driver_position = Column(Integer, nullable=True)
    position_text = Column(String(2), nullable=True)
    position_order = Column(Integer, nullable=True)
    driver_rank = Column(Integer, nullable=True)
    milliseconds = Column(Integer, nullable=True)
    fastest_lap = Column(Integer, nullable=True)
    fastest_lap_time = Column(Interval, nullable=True)
    fastest_lap_speed = Column(Float, nullable=True)
    points = Column(Float, nullable=True)

    race = relationship("Race", back_populates="race_results")
    driver = relationship("Driver", back_populates="race_results")
    status = relationship("Status", back_populates="race_results")
    constructor = relationship("Constructor", back_populates="race_results")