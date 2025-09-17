from sqlalchemy import create_engine

# Add echo = True for verbosity
engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/formula_one_db")
