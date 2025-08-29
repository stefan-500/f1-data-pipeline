-- Create tables

CREATE TABLE dim_status (
 	status_id serial,
 	status varchar(20),
  	PRIMARY KEY (status_id)
);

CREATE TABLE dim_time (
	time_id serial,
	time_year varchar(4),
	time_date date,
	time_of_day time,
	PRIMARY KEY(time_id)
);

CREATE TABLE dim_circuits (
	circuit_id serial,
	circuit_ref varchar(20),
	circuit_name varchar(50),
	url varchar(100),
	circuit_location varchar(45),
	latitude float,
	longitude float,
	altitude integer,
	country varchar(30),
	PRIMARY KEY(circuit_id)
);

CREATE TABLE dim_races (
	race_id serial,
	time_id integer REFERENCES dim_time(time_id),
	circuit_id integer REFERENCES dim_circuits(circuit_id),
	race_name varchar(80),
	url varchar(100),
	round integer,
	PRIMARY KEY(race_id)
);

CREATE TABLE dim_drivers (
	driver_id serial,
	driver_ref varchar(50),
	forename varchar(30),
	sourname varchar(30),
	dob DATE,
	nationality varchar(30),
	url varchar(100),
	driver_num integer,
	code char(3),
	PRIMARY KEY(driver_id)
);

CREATE TABLE dim_constructors (
	constructor_id serial,
	const_ref varchar(50),
	const_name varchar(30),
	nationality varchar(30),
	url varchar(100),
	PRIMARY KEY(constructor_id)
);

CREATE TABLE fact_driver_standings (
	driv_stand_id serial,
	driver_id integer REFERENCES dim_drivers(driver_id),
	constructor_id integer REFERENCES dim_constructors(constructor_id),
	points float,
	driv_position integer,
	position_text varchar(2),
	wins integer,
	PRIMARY KEY(driv_stand_id)
);

CREATE TABLE fact_constructor_standings (
	const_stand_id serial,
	constructor_id integer REFERENCES dim_constructors(constructor_id),
	points float,
	const_position integer,
	position_text varchar(2),
	wins integer,
	PRIMARY KEY(const_stand_id)
);

CREATE TABLE fact_race_results (
	result_id serial,
	race_id integer REFERENCES dim_races(race_id),
	driver_id integer REFERENCES dim_drivers(driver_id),
	status_id integer REFERENCES dim_status(status_id),
	constructor_id integer REFERENCES dim_constructors(constructor_id),
	laps integer,
	passing_time interval,
	car_number integer,
	grid integer,
	driver_position integer,
	position_text varchar(2),
	position_order integer,
	driver_rank integer,
	milliseconds integer,
	fastest_lap integer,
	fastest_lap_time interval,
	fastest_lap_speed float,
	points float,
	PRIMARY KEY(result_id)
);

CREATE TABLE fact_lap_times (
	lt_id serial,
	race_id integer REFERENCES dim_races(race_id),
	driver_id integer REFERENCES dim_drivers(driver_id),
	lap integer,
	lt_position integer,
	passing_time interval,
	milliseconds integer,
	PRIMARY KEY(lt_id)
);

CREATE TABLE fact_pit_stops (
	pt_id serial,
	race_id integer REFERENCES dim_races(race_id),
	driver_id integer REFERENCES dim_drivers(driver_id),
	stop integer,
	lap integer,
	pt_time varchar(20), -- pit stop start time
	duration interval,
	milliseconds integer,
	PRIMARY KEY(pt_id)
);