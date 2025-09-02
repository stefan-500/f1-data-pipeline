# from typing import List
# from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Date, Time
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from base import Base

class Status(Base):
    __tablename__ = "dim_status"

    status_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(20))

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
    # TODO
    circuit: Mapped["Circuit"] = relationship("Circuit", back_populates="dim_races")
    time: Mapped["_Time"] = relationship("_Time", back_populates="dim_races")