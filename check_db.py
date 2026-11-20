import sqlite3
import pandas as pd

conn = sqlite3.connect("vessel.db")
df = pd.read_sql("SELECT * FROM reports LIMIT 10",conn)
print(df)