import pandas as pd

df = pd.read_csv("source/rym_clean1.csv")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(df.head(3).to_string())