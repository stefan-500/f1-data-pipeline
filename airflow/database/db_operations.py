from database.init_db import engine
from sqlalchemy.orm import Session
from sqlalchemy import insert
import pandas as pd
from models.metadata import Status, _Time, Circuit, Race, Constructor, Driver, DriverStanding, ConstructorStanding, LapTime, PitStop, RaceResult
from pathlib import Path
from shutil import rmtree
import logging

def delete_staging_dir():
    staging_dir_path = Path("/opt/airflow/data/staging")

    if staging_dir_path.exists() and staging_dir_path.is_dir():
        rmtree(staging_dir_path)
        logging.info(f"Deleted staging directory: {staging_dir_path}")
    else:
        logging.info(f"Staging directory not found, nothing to delete.")

def import_csv_data():
    file_path = "data/f1Dataset.csv"
    df = pd.read_csv(file_path, low_memory=False, na_values='\\N')
 
    # Replace NaN values with Python None
    df = df.astype(object).where(pd.notnull(df), None)    

    # Drop unnecessary columns
    cols_to_drop = [0, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
    df.drop(df.columns[cols_to_drop], axis=1, inplace=True)

    # Create a dataframe per table

    # STATUS
    df_status = df[['statusId', 'status']].drop_duplicates().sort_values(by='statusId')
    df_status = df_status.reset_index(drop=True)

    # TIME
    df_time = df[['year', 'date', 'time_races']].drop_duplicates().sort_values(by=['year', 'date'])
    df_time = df_time.reset_index(drop=True)
    # Add time_id, an integer representation of time_date
    df_time['date'] = pd.to_datetime(df_time['date']) # has to be type datetime
    df_time['time_id'] = df_time['date'].dt.strftime('%Y%m%d').astype(int)

    # CIRCUITS
    df_circuits = df[['circuitId', 'circuitRef', 'name_y', 'url_y', 'location', 'country', 'lat', 'lng', 'alt']].drop_duplicates().sort_values(by='circuitId')
    # name_y => circuit name
    # url_y => circuit url
    df_circuits = df_circuits.reset_index(drop=True)

    # RACES
    df_races = df[['raceId', 'name_x', 'url_x', 'round', 'circuitId', 'date']].drop_duplicates().sort_values(by='raceId')
    # date is temporary, has to be type datetime for merging
    df_races['date'] = pd.to_datetime(df_races['date'])
    df_races = df_races.reset_index(drop=True)

    # Merge time and circuit
    # (every race is held at a unique date)
    df_races = df_races.merge(
        df_time[['date', 'time_id']],
        on='date',
        how='inner'
    )
    df_races = df_races.merge(
        df_circuits[['circuitId']],
        on='circuitId',
        how='inner'
    )

    df_races.drop(columns=['date'], inplace=True)

    # DRIVERS
    df_drivers = df[['driverId', 'driverRef', 'forename', 'surname', 'dob', 'nationality', 'url', 'number_drivers', 'code']].drop_duplicates().sort_values(by='driverId')
    df_drivers = df_drivers.reset_index(drop=True)

    # CONSTRUCTORS
    df_constructors = df[['constructorId', 'constructorRef', 'name', 'nationality_constructors', 'url_constructors']].drop_duplicates().sort_values(by='constructorId')
    df_constructors = df_constructors.reset_index(drop=True)

    # DRIVER STANDINGS
    df_dstandings = df[['driverStandingsId', 'raceId', 'driverId', 'constructorId', 'points_driverstandings', 'position_driverstandings', 'positionText_driverstandings', 'wins']].drop_duplicates().sort_values(by='driverStandingsId')
    df_dstandings = df_dstandings.reset_index(drop=True)

    # Merge race, driver and constructor
    df_dstandings = df_dstandings.merge(
        df_races[['raceId']],
        on='raceId',
        how='inner'
    )
    df_dstandings = df_dstandings.merge(
        df_drivers[['driverId']],
        on='driverId',
        how='inner'
    )
    df_dstandings = df_dstandings.merge(
        df_constructors[['constructorId']],
        on='constructorId',
        how='inner'
    )

    # CONSTRUCTOR STANDINGS
    df_cstandings = df[['constructorStandingsId', 'raceId', 'constructorId', 'points_constructorstandings', 'position_constructorstandings', 'positionText_constructorstandings', 'wins_constructorstandings']].drop_duplicates().sort_values(by='constructorStandingsId')
    df_cstandings = df_cstandings.reset_index(drop=True)

    # Merge race and constructor
    df_cstandings = df_cstandings.merge(
        df_races[['raceId']],
        on='raceId',
        how='inner'
    )
    df_cstandings = df_cstandings.merge(
        df_constructors[['constructorId']],
        on='constructorId',
        how='inner'
    )

    # LAP TIMES
    df_laps = df[['raceId', 'driverId', 'lap', 'position_laptimes', 'time_laptimes', 'milliseconds_laptimes']].drop_duplicates().sort_values(by=['raceId', 'driverId', 'lap'])
    df_laps = df_laps.reset_index(drop=True)

    # Merge race and driver
    df_laps = df_laps.merge(
        df_races[['raceId']],
        on='raceId',
        how='inner'
    )
    df_laps = df_laps.merge(
        df_drivers[['driverId']],
        on='driverId',
        how='inner'
    )

    # PIT STOPS
    df_stops = df[['raceId', 'driverId', 'stop', 'lap_pitstops', 'time_pitstops', 'duration', 'milliseconds_pitstops']].drop_duplicates().sort_values(by=['raceId', 'driverId', 'stop'])
    df_stops = df_stops.reset_index(drop=True)

    # Merge race and driver
    df_stops = df_stops.merge(
        df_races[['raceId']],
        on='raceId',
        how='inner'
    )
    df_stops = df_stops.merge(
        df_drivers[['driverId']],
        on='driverId',
        how='inner'
    )

    # RACE RESULTS
    df_results = df[['resultId', 'raceId', 'driverId', 'statusId', 'constructorId', 'laps', 'time', 'number', 'grid', 'position', 'positionText',
    'positionOrder', 'rank', 'milliseconds', 'fastestLap', 'fastestLapTime', 'fastestLapSpeed', 'points']].drop_duplicates().sort_values(by=['resultId'])
    df_results = df_results.reset_index(drop=True)

    # Merge race, driver, status and constructor
    df_results = df_results.merge(
        df_races[['raceId']],
        on='raceId',
        how='inner'
    )
    df_results = df_results.merge(
        df_drivers[['driverId']],
        on='driverId',
        how='inner'
    )
    df_results = df_results.merge(
        df_status[['statusId']],
        on='statusId',
        how='inner'
    )
    df_results = df_results.merge(
        df_constructors[['constructorId']],
        on='constructorId',
        how='inner'
    )
    
    # Rename df columns to match Class attributes
    df_status = df_status.rename(columns={
        'statusId': 'status_id'
    })
                   
    df_time = df_time.rename(columns={
        'year': 'time_year',
        'date': 'time_date',
        'time_races': 'time_of_day',
    })

    df_circuits = df_circuits.rename(columns={
        'circuitId': 'circuit_id',
        'circuitRef': 'circuit_ref',
        'name_y': 'circuit_name',
        'url_y': 'url',
        'location': 'circuit_location',
        'lat': 'latitude',
        'lng': 'longitude',
        'alt': 'altitude'
    })

    df_races = df_races.rename(columns={
        'raceId': 'race_id',
        'circuitId': 'circuit_id',
        'name_x': 'race_name',
        'url_x': 'url',
    })

    df_drivers = df_drivers.rename(columns={
        'driverId': 'driver_id',
        'driverRef': 'driver_ref',
        'number_drivers': 'driver_num',
    })

    df_constructors = df_constructors.rename(columns={
        'constructorId': 'constructor_id',
        'constructorRef': 'const_ref',
        'name': 'const_name',
        'nationality_constructors': 'nationality',
        'url_constructors': 'url',
    })

    df_dstandings = df_dstandings.rename(columns={
        'driverStandingsId': 'driv_stand_id',
        'driverId': 'driver_id',
        'constructorId': 'constructor_id',
        'raceId': 'race_id',
        'points_driverstandings': 'points',
        'position_driverstandings': 'driv_position',
        'positionText_driverstandings': 'position_text',
    })
    
    df_cstandings = df_cstandings.rename(columns={
        'constructorStandingsId': 'const_stand_id',
        'constructorId': 'constructor_id',
        'raceId': 'race_id',
        'points_constructorstandings': 'points',
        'position_constructorstandings': 'const_position',
        'positionText_constructorstandings': 'position_text',
        'wins_constructorstandings': 'wins'
    })

    df_laps = df_laps.rename(columns={
        'raceId': 'race_id',
        'driverId': 'driver_id',
        'position_laptimes': 'lt_position',
        'time_laptimes': 'passing_time',
        'milliseconds_laptimes': 'milliseconds',
    })

    df_stops = df_stops.rename(columns={
        'raceId': 'race_id',
        'driverId': 'driver_id',
        'lap_pitstops': 'lap',
        'time_pitstops': 'ps_time',
        'milliseconds_pitstops': 'milliseconds',
    })

    df_results = df_results.rename(columns={
        'resultId': 'result_id',
        'raceId': 'race_id',
        'driverId': 'driver_id',
        'statusId': 'status_id',
        'constructorId': 'constructor_id',
        'time': 'passing_time',
        'number': 'car_number',
        'position': 'driver_position',
        'positionText': 'position_text',
        'positionOrder': 'position_order',
        'rank': 'driver_rank',
        'fastestLap': 'fastest_lap',
        'fastestLapTime': 'fastest_lap_time',
        'fastestLapSpeed': 'fastest_lap_speed',
    })

    # Create staging dir if it does not exist
    staging_dir_path = Path("/opt/airflow/data/staging")
    staging_dir_path.mkdir(parents=True, exist_ok=True)

    # Save a dataframe per table
    df_status.to_parquet(staging_dir_path / "dim_status.parquet")
    df_time.to_parquet(staging_dir_path / "dim_time.parquet")
    df_circuits.to_parquet(staging_dir_path / "dim_circuits.parquet")
    df_races.to_parquet(staging_dir_path / "dim_races.parquet")
    df_drivers.to_parquet(staging_dir_path / "dim_drivers.parquet")
    df_constructors.to_parquet(staging_dir_path / "dim_constructors.parquet")
    df_dstandings.to_parquet(staging_dir_path / "fact_dstandings.parquet")
    df_cstandings.to_parquet(staging_dir_path / "fact_cstandings.parquet")
    df_laps.to_parquet(staging_dir_path / "fact_laps.parquet")
    df_stops.to_parquet(staging_dir_path / "fact_stops.parquet")
    df_results.to_parquet(staging_dir_path / "fact_results.parquet")

def insert_status():
    # Load status from staging/
    file_path = "data/staging/dim_status.parquet"
    df_status = pd.read_parquet(file_path)
    
    # Replace NaN values with Python None
    df_status = df_status.astype(object).where(pd.notnull(df_status), None)

    # Insert Status to db
    with Session(engine) as session:
        try:
            if not df_status.empty:
                # Convert to a list of dictionaries for insert()
                # Each row is a dictionary
                statuses = df_status.to_dict(orient='records')
                
                session.execute(insert(Status), statuses)
                logging.info(f"Inserted {len(statuses)} rows into {Status.__tablename__}")

            session.commit()
            logging.info("Status - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Statuses error, transaction rolled back.", e)
            raise

def insert_time():
    file_path = "data/staging/dim_time.parquet"
    df_time = pd.read_parquet(file_path)
    df_time = df_time.astype(object).where(pd.notnull(df_time), None)

    with Session(engine) as session:
        try:
            if not df_time.empty:
                time = df_time.to_dict(orient='records')

                session.execute(insert(_Time), time)
                logging.info(f"Inserted {len(time)} rows into {_Time.__tablename__}")

            session.commit()
            logging.info("Time - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Time error, transaction rolled back.", e)
            raise

def insert_circuits():
    file_path = "data/staging/dim_circuits.parquet"
    df_circuits = pd.read_parquet(file_path)
    df_circuits = df_circuits.astype(object).where(pd.notnull(df_circuits), None)

    with Session(engine) as session:
        try:
            if not df_circuits.empty:
                circuits = df_circuits.to_dict(orient='records')

                session.execute(insert(Circuit), circuits)
                logging.info(f"Inserted {len(circuits)} rows into {Circuit.__tablename__}")

            session.commit()
            logging.info("Circuit - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Circuits error, transaction rolled back.", e)
            raise

def insert_races():
    file_path = "data/staging/dim_races.parquet"
    df_races = pd.read_parquet(file_path)
    df_races = df_races.astype(object).where(pd.notnull(df_races), None)

    with Session(engine) as session:
        try:
            if not df_races.empty:
                races = df_races.to_dict(orient='records')
                
                session.execute(insert(Race), races)
                logging.info(f"Inserted {len(races)} rows into {Race.__tablename__}")

            session.commit()
            logging.info("Race - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Races error, transaction rolled back.", e)
            raise

def insert_drivers():
    file_path = "data/staging/dim_drivers.parquet"
    df_drivers = pd.read_parquet(file_path)
    df_drivers = df_drivers.astype(object).where(pd.notnull(df_drivers), None)

    with Session(engine) as session:
        try:
            if not df_drivers.empty:
                drivers = df_drivers.to_dict(orient='records')

                session.execute(insert(Driver), drivers)
                logging.info(f"Inserted {len(drivers)} rows into {Driver.__tablename__}")

            session.commit()
            logging.info("Driver - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Drivers error, transaction rolled back.", e)
            raise

def insert_constructors():
    file_path = "data/staging/dim_constructors.parquet"
    df_constructors = pd.read_parquet(file_path)
    df_constructors = df_constructors.astype(object).where(pd.notnull(df_constructors), None)

    with Session(engine) as session:
        try:
            if not df_constructors.empty:
                constructors = df_constructors.to_dict(orient='records')
   
                session.execute(insert(Constructor), constructors)
                logging.info(f"Inserted {len(constructors)} rows into {Constructor.__tablename__}")

            session.commit()
            logging.info("Constructor - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Constructors error, transaction rolled back.", e)
            raise

def insert_driver_standings():
    file_path = "data/staging/fact_dstandings.parquet"
    df_dstandings = pd.read_parquet(file_path)
    df_dstandings = df_dstandings.astype(object).where(pd.notnull(df_dstandings), None)

    with Session(engine) as session:
        try:
            if not df_dstandings.empty:
                dstandings = df_dstandings.to_dict(orient='records')
 
                session.execute(insert(DriverStanding), dstandings)
                logging.info(f"Inserted {len(dstandings)} rows into {DriverStanding.__tablename__}")

            session.commit()
            logging.info("Driver Standings - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Driver Standings error, transaction rolled back.", e)
            raise

def insert_constructor_standings():
    file_path = "data/staging/fact_cstandings.parquet"
    df_cstandings = pd.read_parquet(file_path)
    df_cstandings = df_cstandings.astype(object).where(pd.notnull(df_cstandings), None)

    with Session(engine) as session:
        try:
            if not df_cstandings.empty:
                cstandings = df_cstandings.to_dict(orient='records')

                session.execute(insert(ConstructorStanding), cstandings)
                logging.info(f"Inserted {len(cstandings)} rows into {ConstructorStanding.__tablename__}")

            session.commit()
            logging.info("Constructor Standings - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Constructor Standings error, transaction rolled back.", e)
            raise

def insert_lap_times():
    file_path = "data/staging/fact_laps.parquet"
    df_laps = pd.read_parquet(file_path)
    df_laps = df_laps.astype(object).where(pd.notnull(df_laps), None)

    with Session(engine) as session:
        try:
            if not df_laps.empty:
                laps = df_laps.to_dict(orient='records')

                session.execute(insert(LapTime), laps)
                logging.info(f"Inserted {len(laps)} rows into {LapTime.__tablename__}")

            session.commit()
            logging.info("Lap Times - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Lap Times error, transaction rolled back.", e)
            raise

def insert_pit_stops():
    file_path = "data/staging/fact_stops.parquet"
    df_stops = pd.read_parquet(file_path)
    df_stops = df_stops.astype(object).where(pd.notnull(df_stops), None)

    with Session(engine) as session:
        try:
            if not df_stops.empty:
                stops = df_stops.to_dict(orient='records')

                session.execute(insert(PitStop), stops)
                logging.info(f"Inserted {len(stops)} rows into {PitStop.__tablename__}")

            session.commit()
            logging.info("Pit Stops - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Pit Stops error, transaction rolled back.", e)
            raise

def insert_race_results():
    file_path = "data/staging/fact_results.parquet"
    df_results = pd.read_parquet(file_path)
    df_results = df_results.astype(object).where(pd.notnull(df_results), None)

    with Session(engine) as session:
        try:
            if not df_results.empty:
                results = df_results.to_dict(orient='records')

                session.execute(insert(RaceResult), results)
                logging.info(f"Inserted {len(results)} rows into {RaceResult.__tablename__}")

            session.commit()
            logging.info("Race Result - Success!")

        except Exception as e:
            session.rollback()
            logging.info("Insert Race Results error, transaction rolled back.", e)
            raise

def validate_insert():
    # Count total rows in each table
    with Session(engine) as session:
        rows_status = session.query(Status).count()
        rows_time = session.query(_Time).count()
        rows_circuits = session.query(Circuit).count() 
        rows_races = session.query(Race).count()
        rows_drivers = session.query(Driver).count()
        rows_constructors = session.query(Constructor).count() 
        rows_dstandings = session.query(DriverStanding).count()
        rows_cstandings = session.query(ConstructorStanding).count()
        rows_laps = session.query(LapTime).count() 
        rows_stops = session.query(PitStop).count()
        rows_results = session.query(RaceResult).count()

        logging.info(f"Status total rows: {rows_status}")
        logging.info(f"Time total rows: {rows_time}")
        logging.info(f"Circuits total rows: {rows_circuits}")
        logging.info(f"Races total rows: {rows_races}")
        logging.info(f"Drivers total rows: {rows_drivers}")
        logging.info(f"Constructors total rows: {rows_constructors}")
        logging.info(f"Driver Standings total rows: {rows_dstandings}")
        logging.info(f"Constructors Standings total rows: {rows_cstandings}")
        logging.info(f"Lap Times total rows: {rows_laps}")
        logging.info(f"Pit Stops total rows: {rows_stops}")
        logging.info(f"Race Results total rows: {rows_results}")
