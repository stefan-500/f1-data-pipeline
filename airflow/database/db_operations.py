from models.base import Base
from database.init_db import engine
from sqlalchemy.orm import Session
from sqlalchemy import insert
from sqlalchemy import text
import os
import pandas as pd
from models.metadata import Status, _Time, Circuit, Race, Constructor, Driver, DriverStanding, ConstructorStanding, LapTime, PitStop, RaceResult

def check_conn():
    with Session(engine) as session:
        result = session.execute(text("select 'hello world'"))
        print(result.all())

def import_data() -> pd.DataFrame:

    file_path = "data/f1Dataset.csv"
    df = pd.read_csv(file_path, low_memory=False, na_values='\\N')
 
    # Replace NaN values with Python None
    df = df.astype(object).where(pd.notnull(df), None)    

    # Drop unnecessary columns
    cols_to_drop = [0, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
    df.drop(df.columns[cols_to_drop], axis=1, inplace=True)

    # print(df.info())
    # print("duplicates:", df.duplicated())

    # Create a dataframe per table

    # STATUS
    df_status = df[['statusId', 'status']].drop_duplicates().sort_values(by='statusId')
    df_status = df_status.reset_index(drop=True)
    
    # print(df_status.info())
    # print(df_status.head())

    # TIME
    df_time = df[['year', 'date', 'time_races']].drop_duplicates().sort_values(by=['year', 'date'])
    df_time = df_time.reset_index(drop=True)
    # Add time_id, an integer representation of time_date
    df_time['date'] = pd.to_datetime(df_time['date']) # has to be type datetime
    df_time['time_id'] = df_time['date'].dt.strftime('%Y%m%d').astype(int)

    # print(df_time.info())
    # print(df_time.head())

    # CIRCUITS
    df_circuits = df[['circuitId', 'circuitRef', 'name_y', 'url_y', 'location', 'country', 'lat', 'lng', 'alt']].drop_duplicates().sort_values(by='circuitId')
    # name_y => circuit name
    # url_y => circuit url
    df_circuits = df_circuits.reset_index(drop=True)

    # print(df_circuits.info())
    # print(df_circuits.head())

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
    
    # print(df_races.info())
    # print(df_races.head())

    # DRIVERS
    df_drivers = df[['driverId', 'driverRef', 'forename', 'surname', 'dob', 'nationality', 'url', 'number_drivers', 'code']].drop_duplicates().sort_values(by='driverId')
    df_drivers = df_drivers.reset_index(drop=True)

    # print(df_drivers.info())
    # print(df_drivers.head())

    # CONSTRUCTORS
    df_constructors = df[['constructorId', 'constructorRef', 'name', 'nationality_constructors', 'url_constructors']].drop_duplicates().sort_values(by='constructorId')
    df_constructors = df_constructors.reset_index(drop=True)

    # print(df_constructors.info())
    # print(df_constructors.head())

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

    # print(df_dstandings.info())
    # print(df_dstandings.head())

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

    # print(df_cstandings.info())
    # print(df_cstandings.head())

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

    # print(df_laps.info())
    # print(df_laps.head())

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

    # print(df_stops.info())
    # print(df_stops.head())

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
    
    # print(df_results.info())
    # print(df_results.head())

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

    # A dictionary of dataframes
    return {'status': df_status, 'time': df_time, 'circuits': df_circuits, 'races': df_races, 'drivers': df_drivers, 'constructors': df_constructors,
            'dstandings': df_dstandings, 'cstandings': df_cstandings, 'laps': df_laps, 'stops': df_stops, 'race_results': df_results}

def insert_data():

    dfs = import_data()

    # Map dict keys to model classes
    insert_order = [
        ('status', Status),
        ('time', _Time),
        ('circuits', Circuit),
        ('races', Race),
        ('drivers', Driver),
        ('constructors', Constructor),
        ('laps', LapTime),
        ('stops', PitStop),
        ('dstandings', DriverStanding),
        ('cstandings', ConstructorStanding),
        ('race_results', RaceResult)
    ]

    # Bulk insert dataframes to db
    with Session(engine) as session:
        try:
            for key, model in insert_order:
                
                df = dfs.get(key) # gets a dataframe by the key
                # print(df)

                if not df.empty:
                    # Convert to a list of dictionaries for insert()
                    # Each row is a dictionary
                    records = df.to_dict(orient='records')
                    
                    # print("\n- - - - - -  - - - -  -- -  - - - - - -")
                    # print(model)
                    # print(records[0].keys())
                    # print("Row 1: ", records[0])
                    # print("- - - - - -  - - - -  -- -  - - - - - -")

                    # Insert data into the table
                    session.execute(insert(model), records)
                    print(f"Inserted {len(records)} rows into {model.__tablename__}\n")

            session.commit()
            print("All tables inserted successfully.")

        except Exception as e:
            session.rollback()
            print("An error occurred, transaction rolled back.\n", e)
            raise
