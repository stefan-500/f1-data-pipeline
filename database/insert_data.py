from models.base import Base
from database.init_db import engine
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd

def check_conn():
    with Session(engine) as session:
        result = session.execute(text("select 'hello world'"))
        print(result.all())

# Read CSV file
# df = pd.read_csv("path/to/file")

# Remove unnecessary columns


def insert_data():
    pass