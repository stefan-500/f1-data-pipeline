from models.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List
from sqlalchemy import String, Date, Time, Float, Interval
from datetime import date, time, timedelta
from sqlalchemy import ForeignKey

class Status(Base):
    __tablename__ = "dim_status"

    status_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(20))
    # TODO
    race_results: Mapped[List["RaceResult"]] = relationship(back_populates="dim_status")

class _Time(Base):
    __tablename__ = "dim_time"

    time_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    time_year: Mapped[str] = mapped_column(String(4))
    time_date: Mapped[date] = mapped_column(Date)
    time_of_day: Mapped[time] = mapped_column(Time)

class Circuit(Base):
    __tablename__ = "dim_circuits"

    circuit_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    circuit_ref: Mapped[str] = mapped_column(String(20))
    circuit_name: Mapped[str] = mapped_column(String(50))
    url: Mapped[str] = mapped_column(String(100))
    circuit_location: Mapped[str] = mapped_column(String(45))
    latitude: Mapped[float]
    longitude: Mapped[float]
    altitude: Mapped[int]
    country: Mapped[str] = mapped_column(String(30))

class Race(Base):
    __tablename__ = "dim_races"

    race_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    time_id: Mapped[int] = mapped_column(ForeignKey('dim_time.time_id'))
    circuit_id: Mapped[int] = mapped_column(ForeignKey('dim_circuits.circuit_id'))
    race_name: Mapped[str] = mapped_column(String(80))
    url: Mapped[str] = mapped_column(String(100))
    round: Mapped[int]
    circuit: Mapped["Circuit"] = relationship("Circuit", back_populates="dim_races")
    time: Mapped["_Time"] = relationship("_Time", back_populates="dim_races")
    # TODO
    driver_standings: Mapped[List["DriverStanding"]] = relationship(back_populates="dim_races")
    lap_times: Mapped[List["LapTime"]] = relationship(back_populates="dim_races")
    pit_stops: Mapped[List["PitStop"]] = relationship(back_populates="dim_races")
    race_result: Mapped["RaceResult"] = relationship(back_populates="dim_races")

class Constructor(Base):
    __tablename__ = "dim_constructors"

    constructor_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    const_ref: Mapped[str] = mapped_column(String(50))
    const_name: Mapped[str] = mapped_column(String(30))
    nationality: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(100))
    # TODO
    driver_standing: Mapped["DriverStanding"] = relationship(back_populates="dim_constructors")
    # A constructor can be located in many const standings (new const standing list after every race)
    constructor_standings: Mapped[List["ConstructorStanding"]] = relationship(back_populates="dim_constructors")
    race_results: Mapped[List["RaceResult"]] = relationship(back_populates="dim_constructors")

class Driver(Base):
    __tablename__ = "dim_drivers"

    driver_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    driver_ref: Mapped[str] = mapped_column(String(50))
    forename: Mapped[str] = mapped_column(String(30))
    sourname: Mapped[str] = mapped_column(String(30))
    dob:  Mapped[date] = mapped_column(Date)
    nationality: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(100))
    driver_num: Mapped[int]
    code: Mapped[str] = mapped_column(String(3))
    # TODO
    driver_standings: Mapped[List["DriverStanding"]] = relationship(back_populates="dim_drivers")
    lap_times: Mapped[List["LapTime"]] = relationship(back_populates="dim_drivers")
    pit_stops: Mapped[List["PitStop"]] = relationship(back_populates="dim_drivers")
    race_results: Mapped[List["RaceResult"]] = relationship(back_populates="dim_drivers")

class DriverStanding(Base):
    __tablename__ = "fact_driver_standings"

    driv_stand_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_drivers.driver_id')) # BUG
    constructor_id: Mapped[int] = mapped_column(ForeignKey('dim_constructors.constructor_id'))
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    points: Mapped[float] = mapped_column(Float(precision=1)) # TODO set as in race_results? 
    driv_position: Mapped[int]
    position_text: Mapped[str] = mapped_column(String(2))
    wins: Mapped[int]
    # TODO
    driver: Mapped["Driver"] = relationship("Driver", back_populates="fact_driver_standings")
    constructors: Mapped[List["Constructor"]] = relationship("Constructor", back_populates="fact_driver_standings")
    race: Mapped["Race"] = relationship("Race", back_populates="fact_driver_standings")

class ConstructorStanding(Base):
    __tablename__ = "fact_constructor_standings"

    const_stand_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    constructor_id: Mapped[int] = mapped_column(ForeignKey('dim_constructors.constructor_id'))
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    points: Mapped[float] = mapped_column(Float(precision=1)) # TODO set as in race_results?
    const_position: Mapped[int]
    position_text: Mapped[str] = mapped_column(String(2))
    wins: Mapped[int]
    # TODO
    constructor: Mapped["Constructor"] = relationship("Constructor", back_populates="fact_constructor_standings")
    race: Mapped["Race"] = relationship("Race", back_populates="fact_constructor_standings")
    
class LapTime(Base):
    __tablename__ = "fact_lap_times"

    lt_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_drivers.driver_id'))
    lap: Mapped[int]
    lt_position: Mapped[int]
    passing_time: Mapped[timedelta] = mapped_column(Interval) 
    milliseconds: Mapped[int]
    # TODO
    race: Mapped["Race"] = relationship("Race", back_populates="fact_lap_times")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="fact_lap_times")

class PitStop(Base):
    __tablename__ = "fact_pit_stops"

    ps_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_drivers.driver_id'))
    stop: Mapped[int]
    lap: Mapped[int]
    ps_time: Mapped[time] = mapped_column(Time) # start time
    duration: Mapped[timedelta] = mapped_column(Interval)
    milliseconds: Mapped[int]
    # TODO
    race: Mapped["Race"] = relationship("Race", back_populates="fact_pit_stops")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="fact_pit_stops")

class RaceResult(Base):
    __tablename__ = "fact_race_results"

    result_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_drivers.driver_id'))
    status_id: Mapped[int] = mapped_column(ForeignKey('dim_status.status_id'))
    constructor_id: Mapped[int] = mapped_column(ForeignKey('dim_constructors.constructor_id'))
    laps: Mapped[int]
    passing_time: Mapped[timedelta] = mapped_column(Interval) # timedelta is compatible with postgres Interval
    car_number: Mapped[int]
    grid: Mapped[int]
    driver_position: Mapped[int]
    position_text: Mapped[str] = mapped_column(String(2))
    position_order: Mapped[int]
    driver_rank: Mapped[int]
    milliseconds: Mapped[int]
    fastest_lap: Mapped[int]
    fastest_lap_time: Mapped[timedelta] = mapped_column(Interval)
    fastest_lap_speed: Mapped[float]
    points: Mapped[float]
    # TODO
    race: Mapped["Race"] = relationship("Race", back_populates="fact_race_results")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="fact_race_results")
    status: Mapped["Status"] = relationship("Status", back_populates="fact_race_results")
    constructor: Mapped["Constructor"] = relationship("Constructor", back_populates="fact_race_results")

        
    