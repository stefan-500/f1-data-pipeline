from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from database.db_operations import (
    prepare_csv_data,
    insert_status,
    insert_time,
    insert_circuits,
    insert_races,
    insert_drivers,
    insert_constructors,
    insert_driver_standings,
    insert_constructor_standings,
    insert_lap_times,
    insert_pit_stops,
    insert_race_results,
    insert_quali_dates,
    validate_insert
)
from api.api_scraper import scrape_data
from datetime import datetime

args = {
    'owner': 'Stefan'
}

with DAG(
    dag_id="f1_data_pipeline",
    description="ETL pipeline that ingests F1 data from CSV file and API, and stores it into the database.",
    start_date=datetime(2025, 9, 11),
    schedule=None,
    catchup=False,
    tags=["ETL", "Formula1"]
) as dag:

    prepare_csv = PythonOperator(
        task_id="prepare_csv_data",
        python_callable=prepare_csv_data
    )

    prepare_api = PythonOperator(
        task_id="prepare_api_data",
        python_callable=scrape_data
    )

    insert_to_status = PythonOperator(
        task_id="insert_status",
        python_callable=insert_status
    )

    insert_to_time = PythonOperator(
        task_id="insert_time",
        python_callable=insert_time
    )

    insert_to_circuits = PythonOperator(
        task_id="insert_circuits",
        python_callable=insert_circuits
    )

    insert_to_races = PythonOperator(
        task_id="insert_races",
        python_callable=insert_races
    )

    insert_to_quali_dates = PythonOperator(
        task_id="insert_quali_dates",
        python_callable=insert_quali_dates
    )

    insert_to_drivers = PythonOperator(
        task_id="insert_drivers",
        python_callable=insert_drivers
    )

    insert_to_constructors = PythonOperator(
        task_id="insert_constructors",
        python_callable=insert_constructors
    )

    insert_to_driver_standings = PythonOperator(
        task_id="insert_driver_standings",
        python_callable=insert_driver_standings
    )

    insert_to_constructor_standings = PythonOperator(
        task_id="insert_constructor_standings",
        python_callable=insert_constructor_standings
    )

    insert_to_lap_times = PythonOperator(
        task_id="insert_lap_times",
        python_callable=insert_lap_times
    )

    insert_to_pit_stops = PythonOperator(
        task_id="insert_pit_stops",
        python_callable=insert_pit_stops
    )

    insert_to_race_results = PythonOperator(
        task_id="insert_race_results",
        python_callable=insert_race_results
    )

    validate = PythonOperator(
        task_id="validate_insert",
        python_callable=validate_insert
    )

    (
    prepare_csv
    >> prepare_api
    >> [insert_to_status, insert_to_time, insert_to_circuits, insert_to_constructors, insert_to_drivers]
    >> insert_to_races
    >> insert_to_quali_dates
    >> [insert_to_driver_standings, insert_to_constructor_standings, insert_to_lap_times, insert_to_pit_stops, insert_to_race_results]
    >> validate
    )

