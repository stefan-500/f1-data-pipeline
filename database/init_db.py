from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

db_pass = os.getenv("DB_PASSWORD") 
engine = create_engine(f"postgresql+psycopg2://postgres:{db_pass}@localhost:5432/test_formula_one_db_1") # add echo = True for verbosity
