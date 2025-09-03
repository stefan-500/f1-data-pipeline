from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import String, Date, Time
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from base import Base
from facts import DriverStanding, ConstructorStanding, LapTime, PitStop, RaceResult

class Status(Base):
    __tablename__ = "dim_status"

    status_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(20))
    # TODO
    race_results: Mapped[List["RaceResult"]] = relationship(back_populates="dim_status")

class _Time(Base):
    __tablename__ = "dim_time"

    time_id: Mapped[int] = mapped_column(primary_key=True)
    time_year: Mapped[str] = mapped_column(String(4))
    time_date: Mapped[Date]
    time_of_day: Mapped[Time]

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
    dob:  Mapped[Date]
    nationality: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(100))
    driver_num: Mapped[int]
    code: Mapped[str] = mapped_column(String(3))
    # TODO
    driver_standings: Mapped[List["DriverStanding"]] = relationship(back_populates="dim_drivers")
    lap_times: Mapped[List["LapTime"]] = relationship(back_populates="dim_drivers")
    pit_stops: Mapped[List["PitStop"]] = relationship(back_populates="dim_drivers")
    race_results: Mapped[List["RaceResult"]] = relationship(back_populates="dim_drivers")