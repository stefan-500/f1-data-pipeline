-- Import CSV data to db by using a staging table

-- Temporary table for initial CSV data import
CREATE TABLE staging (
	first_col integer,
	result_id integer,
 	race_id integer,
	driver_id integer,
	constructor_id integer,
	car_number integer,
	grid int,
	car_position integer,
	position_text varchar(2),
	position_order integer,
	points float,
	lap integer,
	passing_time varchar(15),
	milliseconds integer,
	fastest_lap integer,
	driver_rank integer,
	fastest_lap_time varchar(15),
	fastest_lap_speed float,
	status_id integer,
	time_year varchar(4),
	round integer,
	circuit_id integer,
	race_name varchar(80),
	time_date date,
	time_of_day time,
	race_url varchar(100),
	fp1_date varchar(50),
	fp1_time varchar(50),
	fp2_date varchar(50),
	fp2_time varchar(50),
	fp3_date varchar(50),
	fp3_time varchar(50),
	quali_date varchar(50),
	quali_time varchar(50),
	sprint_date varchar(50),
	sprint_time varchar(50),
	circuit_ref varchar(20),
	circuit_name varchar(50),
	circuit_location varchar(45),
	country varchar(30),
	latitude float,
	longitude float,
	altitude integer, -- \N?
	circuit_url varchar(100),
	driver_ref varchar(50),
	driver_num integer,
	code char(3),
	forename varchar(30),
	sourname varchar(30),
	dob DATE,
	driver_nationality varchar(30),
	driver_url varchar(100),
	const_ref varchar(50),
	const_name varchar(30),
	const_nationality varchar(30),
	const_url varchar(100),
	lt_lap integer,
	lt_position integer,
	lt_passing_time interval,
	lt_milliseconds integer,
	stop integer,
	ps_lap integer,
	ps_time varchar(20),
	ps_duration interval,
	ps_milliseconds integer,
	driv_stand_id integer,
	ds_points float,
	ds_position integer,
	ds_position_text varchar(2),
	ds_wins integer,
	const_stand_id integer,
	cs_points float,
	cs_position integer,
	cs_position_text varchar(2),
	cs_wins integer,
	status varchar(20)
);

-- Import data from CSV file to staging table
-- Paste the command into psql shell, adjust file path
\COPY staging(first_col, result_id, race_id, driver_id, constructor_id, car_number, grid, car_position, position_text, position_order, points, lap, passing_time, milliseconds, fastest_lap, driver_rank, fastest_lap_time, fastest_lap_speed, status_id, time_year, round, circuit_id, race_name, time_date, time_of_day, race_url, fp1_date, fp1_time, fp2_date, fp2_time, fp3_date, fp3_time, quali_date, quali_time, sprint_date, sprint_time, circuit_ref, circuit_name, circuit_location, country, latitude, longitude, altitude, circuit_url, driver_ref, driver_num, code, forename, sourname, dob, driver_nationality, driver_url, const_ref, const_name, const_nationality, const_url, lt_lap, lt_position, lt_passing_time, lt_milliseconds, stop, ps_lap, ps_time, ps_duration, ps_milliseconds, driv_stand_id, ds_points, ds_position, ds_position_text, ds_wins, const_stand_id, cs_points, cs_position, cs_position_text, cs_wins, status) FROM 'path\to\file' DELIMITER ',' CSV HEADER NULL AS '\N' ENCODING 'utf8';

-- Drop unnecessary columns
ALTER TABLE staging
DROP COLUMN first_col,
DROP COLUMN fp1_date,
DROP COLUMN fp1_time,
DROP COLUMN fp2_date,
DROP COLUMN fp2_time,
DROP COLUMN fp3_date,
DROP COLUMN fp3_time,
DROP COLUMN quali_date,
DROP COLUMN quali_time,
DROP COLUMN sprint_date,
DROP COLUMN sprint_time;

-- Distribute columns to relevant tables

-- STATUS
-- SELECT DISTINCT status_id, status FROM staging;
-- SELECT * from dim_status;

INSERT INTO dim_status(status_id, status)
SELECT DISTINCT s.status_id, s.status
FROM staging s
ORDER BY s.status_id; -- identical order

-- TIME
-- SELECT DISTINCT time_year, time_date, time_of_day FROM staging 
-- ORDER BY time_year, time_date;

-- SELECT * FROM dim_time;

INSERT INTO dim_time(time_year, time_date, time_of_day) -- PK is auto-increment 
SELECT DISTINCT s.time_year, s.time_date, s.time_of_day
FROM staging s
ORDER BY time_year, time_date;

-- CIRCUITS
-- SELECT DISTINCT circuit_id, circuit_ref, circuit_name, circuit_url, circuit_location,
-- latitude, longitude, altitude, country FROM staging;

-- SELECT * FROM dim_circuits;

INSERT INTO dim_circuits(circuit_id, circuit_ref, circuit_name, url, circuit_location,
latitude, longitude, altitude, country)
SELECT DISTINCT s.circuit_id, s.circuit_ref, s.circuit_name, s.circuit_url, s.circuit_location,
s.latitude, s.longitude, s.altitude, s.country
FROM staging s
ORDER BY s.circuit_id;

-- RACES
-- SELECT DISTINCT race_id, time_date, circuit_id, race_name, race_url, round
-- FROM staging
-- ORDER BY race_id;

-- SELECT dr.race_id, dr.time_id, dt.time_date, dt.time_year, dt.time_of_day, dr.circuit_id, dc.circuit_name,
-- dr.round, dr.url
-- FROM dim_races dr
-- INNER JOIN dim_time dt ON dt.time_id = dr.time_id
-- INNER JOIN dim_circuits dc ON dc.circuit_id = dr.circuit_id;

INSERT INTO dim_races(race_id, time_id, circuit_id, race_name, url, round)
SELECT DISTINCT s.race_id, dt.time_id, dc.circuit_id, s.race_name, s.race_url, s.round
FROM staging s
INNER JOIN dim_time dt ON dt.time_date = s.time_date
INNER JOIN dim_circuits dc ON dc.circuit_id = s.circuit_id;

-- DRIVERS
-- SELECT DISTINCT driver_id, driver_ref, forename, sourname, dob,
-- driver_nationality, driver_url, driver_num, code FROM staging
-- ORDER BY driver_id;

-- SELECT * FROM dim_drivers;

INSERT INTO dim_drivers(driver_id, driver_ref, forename, sourname, dob, nationality, url, driver_num, code)
SELECT DISTINCT s.driver_id, s.driver_ref, s.forename, s.sourname, s.dob,
s.driver_nationality, s.driver_url, s.driver_num, s.code 
FROM staging s
ORDER BY driver_id;

-- CONSTRUCTORS
-- SELECT DISTINCT constructor_id, const_ref, const_name, const_nationality, const_url
-- FROM staging
-- ORDER BY constructor_id;

-- SELECT * FROM dim_constructors;

INSERT INTO dim_constructors(constructor_id, const_ref, const_name, nationality, url)
SELECT DISTINCT s.constructor_id, s.const_ref, s.const_name, s.const_nationality, s.const_url
FROM staging s
ORDER BY constructor_id;

-- DRIVER STANDINGS
-- SELECT DISTINCT driv_stand_id, driver_id, constructor_id, ds_points, ds_position, ds_position_text, ds_wins
-- FROM staging
-- ORDER BY driv_stand_id;

-- SELECT * FROM fact_driver_standings;

INSERT INTO fact_driver_standings(driv_stand_id, driver_id, constructor_id, points, driv_position, position_text, wins)
SELECT DISTINCT s.driv_stand_id, dd.driver_id, dc.constructor_id, s.ds_points, s.ds_position, ds_position_text, ds_wins
FROM staging s
INNER JOIN dim_drivers dd ON dd.driver_id = s.driver_id
INNER JOIN dim_constructors dc ON dc.constructor_id = s.constructor_id
ORDER BY driv_stand_id;

-- CONSTRUCTOR STANDINGS
-- SELECT DISTINCT const_stand_id, constructor_id, cs_points, cs_position, cs_position_text, cs_wins
-- FROM staging
-- ORDER BY const_stand_id;

-- SELECT * FROM fact_constructor_standings;

INSERT INTO fact_constructor_standings(const_stand_id, constructor_id, points, const_position, position_text, wins)
SELECT DISTINCT s.const_stand_id, s.constructor_id, s.cs_points, s.cs_position, s.cs_position_text, s.cs_wins
FROM staging s
INNER JOIN dim_constructors dc ON dc.constructor_id = s.constructor_id
ORDER BY const_stand_id;

-- LAP TIMES
-- SELECT DISTINCT race_id, race_name, driver_id, lt_lap, lt_position, lt_passing_time, lt_milliseconds
-- FROM staging
-- ORDER BY race_id;

-- SELECT * FROM fact_lap_times;

INSERT INTO fact_lap_times(race_id, driver_id, lap, lt_position, passing_time, milliseconds)
SELECT DISTINCT s.race_id, s.driver_id, s.lt_lap, s.lt_position, s.lt_passing_time, s.lt_milliseconds
FROM staging s
INNER JOIN dim_races dr ON dr.race_id = s.race_id
INNER JOIN dim_drivers dd ON dd.driver_id = s.driver_id
ORDER BY s.race_id;

-- PIT STOPS
-- SELECT DISTINCT race_id, race_name, driver_id, stop, ps_lap, ps_time, ps_duration, ps_milliseconds
-- FROM staging
-- ORDER BY race_id;

-- SELECT * FROM fact_pit_stops;

INSERT INTO fact_pit_stops(race_id, driver_id, stop, lap, pt_time, duration, milliseconds)
SELECT DISTINCT s.race_id, s.driver_id, s.stop, s.ps_lap, s.ps_time, s.ps_duration, s.ps_milliseconds
FROM staging s
INNER JOIN dim_races dr ON dr.race_id = s.race_id
INNER JOIN dim_drivers dd ON dd.driver_id = s.driver_id
ORDER BY race_id;

-- RACE RESULTS