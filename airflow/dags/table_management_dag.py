from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from database.table_management import create_tables, drop_tables

args = {
    'owner': 'Stefan'
}

with DAG(
    dag_id="db_reset_create",
    description="Deletes all database tables and recreates them from metadata."
    # schedule_interval=None
) as dag:
    
    drop_tables = PythonOperator(
        task_id="drop_all_tables",
        python_callable=drop_tables
    )

    create_tables = PythonOperator(
        task_id="create_all_tables",
        python_callable=create_tables
    )

    drop_tables >> create_tables