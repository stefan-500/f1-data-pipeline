from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from database.db_operations import import_data, insert_data
from datetime import datetime

args = {
    'owner': 'Stefan'
}

with DAG(
    dag_id="csv_to_db",
    description="Loads data from CSV file and inserts it into database.",
    start_date=datetime(2025, 9, 11),
    schedule=None,
    catchup=False
) as dag:

    insert_to_db = PythonOperator(
        task_id="import_and_insert",
        python_callable=insert_data
    )