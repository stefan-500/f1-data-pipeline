from models.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List
from sqlalchemy.types import Integer, String, Date, Time, Float, Interval, CHAR
from datetime import date, time, timedelta
from sqlalchemy import ForeignKey

class Status(Base):
    __tablename__ = "dim_status"

    status_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(20), nullable=True)

    race_results: Mapped[List["RaceResult"]] = relationship(back_populates="status")

class _Time(Base):
    __tablename__ = "dim_time"

    time_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    time_year: Mapped[str] = mapped_column(String(4), nullable=True)
    time_date: Mapped[date] = mapped_column(Date, nullable=True)
    time_of_day: Mapped[time] = mapped_column(Time, nullable=True)

    race: Mapped["Race"] = relationship("Race", back_populates="time")

class Circuit(Base):
    __tablename__ = "dim_circuits"

    circuit_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    circuit_ref: Mapped[str] = mapped_column(String(20), nullable=True)
    circuit_name: Mapped[str] = mapped_column(String(50), nullable=True)
    url: Mapped[str] = mapped_column(String(100), nullable=True)
    circuit_location: Mapped[str] = mapped_column(String(45), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    altitude: Mapped[int] = mapped_column(Integer, nullable=True)
    country: Mapped[str] = mapped_column(String(30), nullable=True)

    race: Mapped["Race"] = relationship("Race", back_populates="circuit")

class Race(Base):
    __tablename__ = "dim_races"

    race_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    time_id: Mapped[int] = mapped_column(ForeignKey('dim_time.time_id'))
    circuit_id: Mapped[int] = mapped_column(ForeignKey('dim_circuits.circuit_id'))
    race_name: Mapped[str] = mapped_column(String(80), nullable=True)
    url: Mapped[str] = mapped_column(String(100), nullable=True)
    
    round: Mapped[int] = mapped_column(Integer, nullable=True)
    circuit: Mapped["Circuit"] = relationship("Circuit", back_populates="dim_races")
    time: Mapped["_Time"] = relationship("_Time", back_populates="dim_races")
    time: Mapped["_Time"] = relationship("_Time", back_populates="race")
    circuit: Mapped["Circuit"] = relationship("Circuit", back_populates="race")
    driver_standings: Mapped[List["DriverStanding"]] = relationship("DriverStanding", back_populates="race")
    constructor_standings: Mapped[List["ConstructorStanding"]] = relationship("ConstructorStanding", back_populates="race")
    lap_times: Mapped[List["LapTime"]] = relationship("LapTime", back_populates="race")
    pit_stops: Mapped[List["PitStop"]] = relationship("PitStop", back_populates="race")
    race_result: Mapped["RaceResult"] = relationship("RaceResult", back_populates="race")

class Constructor(Base):
    __tablename__ = "dim_constructors"

    constructor_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    const_ref: Mapped[str] = mapped_column(String(50), nullable=True)
    const_name: Mapped[str] = mapped_column(String(30), nullable=True)
    nationality: Mapped[str] = mapped_column(String(30), nullable=True)
    url: Mapped[str] = mapped_column(String(100), nullable=True)

    driver_standing: Mapped["DriverStanding"] = relationship("DriverStanding", back_populates="constructors")
    # A constructor can be located in many const standings (new const standing list after every race)
    constructor_standings: Mapped[List["ConstructorStanding"]] = relationship("ConstructorStanding", back_populates="constructor")
    race_results: Mapped[List["RaceResult"]] = relationship("RaceResult", back_populates="constructor")

class Driver(Base):
    __tablename__ = "dim_drivers"

    driver_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    driver_ref: Mapped[str] = mapped_column(String(50), nullable=True)
    forename: Mapped[str] = mapped_column(String(30), nullable=True)
    surname: Mapped[str] = mapped_column(String(30), nullable=True)
    dob:  Mapped[date] = mapped_column(Date, nullable=True)
    nationality: Mapped[str] = mapped_column(String(30), nullable=True)
    url: Mapped[str] = mapped_column(String(100), nullable=True)
    driver_num: Mapped[int] = mapped_column(Integer, nullable=True)
    code: Mapped[str] = mapped_column(CHAR(3), nullable=True)

    driver_standings: Mapped[List["DriverStanding"]] = relationship("DriverStanding", back_populates="driver")
    lap_times: Mapped[List["LapTime"]] = relationship("LapTime", back_populates="driver")
    pit_stops: Mapped[List["PitStop"]] = relationship("PitStop", back_populates="driver")
    race_results: Mapped[List["RaceResult"]] = relationship("RaceResult", back_populates="driver")

class DriverStanding(Base):
    __tablename__ = "fact_driver_standings"

    driv_stand_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_drivers.driver_id'))
    constructor_id: Mapped[int] = mapped_column(ForeignKey('dim_constructors.constructor_id'))
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    points: Mapped[float] = mapped_column(Float(precision=1), nullable=True) # TODO set type as in race_results? 
    driv_position: Mapped[int] = mapped_column(Integer, nullable=True)
    position_text: Mapped[str] = mapped_column(String(2), nullable=True)
    wins: Mapped[int] = mapped_column(Integer, nullable=True)

    driver: Mapped["Driver"] = relationship("Driver", back_populates="driver_standings")
    constructors: Mapped[List["Constructor"]] = relationship("Constructor", back_populates="driver_standing")
    race: Mapped["Race"] = relationship("Race", back_populates="driver_standings")

class ConstructorStanding(Base):
    __tablename__ = "fact_constructor_standings"

    const_stand_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    constructor_id: Mapped[int] = mapped_column(ForeignKey('dim_constructors.constructor_id'))
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    points: Mapped[float] = mapped_column(Float(precision=1), nullable=True) # TODO set type as in race_results?
    const_position: Mapped[int] = mapped_column(Integer, nullable=True)
    position_text: Mapped[str] = mapped_column(String(2), nullable=True)
    wins: Mapped[int] = mapped_column(Integer, nullable=True)

    constructor: Mapped["Constructor"] = relationship("Constructor", back_populates="constructor_standings")
    race: Mapped["Race"] = relationship("Race", back_populates="constructor_standings")
    
class LapTime(Base):
    __tablename__ = "fact_lap_times"

    lt_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_drivers.driver_id'))
    lap: Mapped[int] = mapped_column(Integer, nullable=True)
    lt_position: Mapped[int] = mapped_column(Integer, nullable=True)
    passing_time: Mapped[timedelta] = mapped_column(Interval, nullable=True) 
    milliseconds: Mapped[int] = mapped_column(Integer, nullable=True)

    race: Mapped["Race"] = relationship("Race", back_populates="lap_times")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="lap_times")

class PitStop(Base):
    __tablename__ = "fact_pit_stops"

    ps_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_drivers.driver_id'))
    stop: Mapped[int] = mapped_column(Integer, nullable=True)
    lap: Mapped[int] = mapped_column(Integer, nullable=True)
    ps_time: Mapped[time] = mapped_column(Time, nullable=True) # start time
    duration: Mapped[timedelta] = mapped_column(Interval, nullable=True)
    milliseconds: Mapped[int] = mapped_column(Integer, nullable=True)

    race: Mapped["Race"] = relationship("Race", back_populates="pit_stops")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="pit_stops")

class RaceResult(Base):
    __tablename__ = "fact_race_results"

    result_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_drivers.driver_id'))
    status_id: Mapped[int] = mapped_column(ForeignKey('dim_status.status_id'))
    constructor_id: Mapped[int] = mapped_column(ForeignKey('dim_constructors.constructor_id'))
    laps: Mapped[int] = mapped_column(Integer, nullable=True)
    passing_time: Mapped[timedelta] = mapped_column(Interval, nullable=True) # timedelta is compatible with postgres Interval
    car_number: Mapped[int] = mapped_column(Integer, nullable=True)
    grid: Mapped[int] = mapped_column(Integer, nullable=True)
    driver_position: Mapped[int] = mapped_column(Integer, nullable=True)
    position_text: Mapped[str] = mapped_column(String(2), nullable=True)
    position_order: Mapped[int] = mapped_column(Integer, nullable=True)
    driver_rank: Mapped[int] = mapped_column(Integer, nullable=True)
    milliseconds: Mapped[int] = mapped_column(Integer, nullable=True)
    fastest_lap: Mapped[int] = mapped_column(Integer, nullable=True)
    fastest_lap_time: Mapped[timedelta] = mapped_column(Interval, nullable=True)
    fastest_lap_speed: Mapped[float] = mapped_column(Float, nullable=True)
    points: Mapped[float] = mapped_column(Float, nullable=True)

    race: Mapped["Race"] = relationship("Race", back_populates="race_result")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="race_results")
    status: Mapped["Status"] = relationship("Status", back_populates="race_results")
    constructor: Mapped["Constructor"] = relationship("Constructor", back_populates="race_results")

        
    