from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import String, Time, Float, Interval
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from base import Base
from dimensions import Driver, Constructor, Race, Status

class DriverStanding(Base):
    __tablename__ = "fact_driver_standings"

    driv_stand_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_driver.driver_id'))
    constructor_id: Mapped[int] = mapped_column(ForeignKey('dim_constructors.constructor_id'))
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    points: Mapped[float] = mapped_column(Float(precision=1))
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
    points: Mapped[float] = mapped_column(Float(precision=1))
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
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_driver.driver_id'))
    lap: Mapped[int]
    lt_position: Mapped[int]
    passing_time: Mapped[Interval]
    milliseconds: Mapped[int]
    # TODO
    race: Mapped["Race"] = relationship("Race", back_populates="fact_lap_times")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="fact_lap_times")

class PitStop(Base):
    __tablename__ = "fact_pit_stops"

    ps_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_driver.driver_id'))
    stop: Mapped[int]
    lap: Mapped[int]
    ps_time: Mapped[Time] # start time
    duration: Mapped[Interval]
    milliseconds: Mapped[int]
    # TODO
    race: Mapped["Race"] = relationship("Race", back_populates="fact_pit_stops")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="fact_pit_stops")

class RaceResult(Base):
    __tablename__ = "fact_race_results"

    result_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race_id: Mapped[int] = mapped_column(ForeignKey('dim_races.race_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('dim_driver.driver_id'))
    status_id: Mapped[int] = mapped_column(ForeignKey('dim_status.status_id'))
    constructor_id: Mapped[int] = mapped_column(ForeignKey('dim_constructor.constructor_id'))
    laps: Mapped[int]
    passing_time: Mapped[Interval]
    car_number: Mapped[int]
    grid: Mapped[int]
    driver_position: Mapped[int]
    position_text: Mapped[str] = mapped_column(String(2))
    position_order: Mapped[int]
    driver_rank: Mapped[int]
    milliseconds: Mapped[int]
    fastest_lap: Mapped[int]
    fastest_lap_time: Mapped[Interval]
    fastest_lap_speed: Mapped[float]
    points: Mapped[float]
    # TODO
    race: Mapped["Race"] = relationship("Race", back_populates="fact_race_results")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="fact_race_results")
    status: Mapped["Status"] = relationship("Status", back_populates="fact_race_results")
    constructor: Mapped["Constructor"] = relationship("Constructor", back_populates="fact_race_results")

        
    