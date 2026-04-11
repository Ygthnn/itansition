import pandas as pd
import re

df = pd.read_parquet('data/data/DATA1/orders.parquet')
s = df['unit_price'].astype(str)
s_pat = s.str.replace(r'\d+', 'N', regex=True)

print("Pattern $NN:", s[s_pat == '$NN'].head(3).tolist())
print("Pattern NN:", s[s_pat == 'NN'].head(3).tolist())
print("Pattern N$N:", s[s_pat == 'N$N'].head(3).tolist())
print("Pattern NN:", s[s_pat == 'NN'].head(3).tolist())

print("Timestamp samples:")
print(df['timestamp'].head(15).tolist())
