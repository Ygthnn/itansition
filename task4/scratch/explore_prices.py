import pandas as pd
import re

df = pd.read_parquet('data/data/DATA3/orders.parquet')

def parse_price(val):
    s = str(val)

    is_usd = 'USD' in s or '$' in s
   
    s_num = re.sub(r'(\d)\D+(\d+)', r'\1.\2', s)
 
    s_num = re.sub(r'[^\d.]', '', s_num)
    
    try:
        price = float(s_num)
    except:
        return 0.0
    
    if not is_usd:
        price *= 1.2
        
    return round(price, 2)

df['unit_price_parsed'] = df['unit_price'].apply(parse_price)
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
df['paid_price'] = df['quantity'] * df['unit_price_parsed']

print(df[['quantity', 'unit_price', 'unit_price_parsed', 'paid_price']].head(20))
