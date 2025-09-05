import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

file_path = os.getenv("DATASET_PATH")
df = pd.read_csv(file_path, low_memory=False)

print(df.info())

# Drop unnecessary columns
cols_to_drop = [0, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
df.drop(df.columns[cols_to_drop], axis=1, inplace=True)

# print(df.info())
# print(df.columns)
# print("duplicates:", df.duplicated())

# Create a dataframe per table

df_status = df[['statusId', 'status']].drop_duplicates().sort_values(by='statusId')
df_status = df_status.reset_index(drop=True)
# print(df_status.info())

df_time = df[['year', 'date', 'time_races']].drop_duplicates().sort_values(by=['year', 'date'])
df_time = df_time.reset_index(drop=True)
# Add time_id, an integer representation of time_date
df_time['date'] = pd.to_datetime(df_time['date']) # has to be type datetime
df_time['time_id'] = df_time['date'].dt.strftime('%Y%m%d').astype(int)
print(df_time.head(10))

# TODO Insert data to db
