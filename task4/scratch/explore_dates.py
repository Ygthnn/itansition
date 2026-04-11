import pandas as pd

df = pd.read_parquet('data/data/DATA1/orders.parquet')

dates = df['timestamp'].head(15).astype(str)
dates_clean = dates.str.replace(r'[;,]', ' ', regex=True).str.replace(r'\.\s*M\.', 'M', case=False, regex=True)

try:
    parsed = pd.to_datetime(dates_clean, format='mixed', dayfirst=False)
    print("Parsed correctly!")
    print(parsed)
except Exception as e:
    print("Error:", e)
