from models.base import Base
from database.init_db import engine
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import os

def check_conn():
    with Session(engine) as session:
        result = session.execute(text("select 'hello world'"))
        print(result.all())

# def import_dataset():

#     file_path = os.getenv("DATASET_PATH")
#     df = pd.read_csv(file_path, low_memory=False)

#     print(df.head())

# Remove unnecessary columns

def insert_data():
    pass