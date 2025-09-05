from models import metadata
from models.base import Base
from database.init_db import engine

def create_tables():
    try:
        # print("Tables in metadata:", Base.metadata.tables)
        Base.metadata.create_all(engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
    else:
        print("Tables created successfully!")

def drop_tables():
    try:
        Base.metadata.drop_all(engine)
    except Exception as e:
        print(f"Error dropping tables: {e}")
    else:
        print("Tables dropped successfully!")    
