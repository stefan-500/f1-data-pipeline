import pandas as pd

csv_file_path = "csv/file/path"
parquet_file_path = "data/f1Dataset.parquet"

df = pd.read_csv(csv_file_path, index_col=False, low_memory=False)

df.to_parquet(parquet_file_path)