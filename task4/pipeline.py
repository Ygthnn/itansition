import os
import re
import yaml
import base64
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

def parse_price(val):
    s = str(val)
    if pd.isna(val) or s.strip() == '':
        return 0.0
    is_usd = 'USD' in s or '$' in s
    s_num = re.sub(r'(\d)\D+(\d+)', r'\1.\2', s)
    s_num = re.sub(r'[^\d.]', '', s_num)
    try:
        price = float(s_num)
    except:
        return 0.0
    if not is_usd:
        price = price * 1.2
    return price

def get_user_components(users_df):
    users_df = users_df.fillna('')
    records = users_df[['id', 'name', 'address', 'phone', 'email']].to_dict('records')
    n = len(records)
    parent = list(range(n))

    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    for i in range(n):
        r1 = records[i]
        for j in range(i + 1, n):
            r2 = records[j]
            matches = sum(1 for k in ['name', 'address', 'phone', 'email'] if r1[k] == r2[k])
            if matches >= 3:
                union(i, j)

    groups = {}
    for i in range(n):
        root = find(i)
        if root not in groups:
            groups[root] = []
        groups[root].append(records[i]['id'])
        
    return groups

def process_folder(folder_path):
    print(f"Processing {folder_path}...")
    
    # 1. Users
    users_path = os.path.join(folder_path, 'users.csv')
    df_users = pd.read_csv(users_path).drop_duplicates()
    
    user_clusters = get_user_components(df_users)
    user_id_to_canonical = {}
    for canonical_id, ids in user_clusters.items():
        for uid in ids:
            user_id_to_canonical[uid] = canonical_id
            
    num_unique_users = len(user_clusters)

    # 2. Books
    books_path = os.path.join(folder_path, 'books.yaml')
    with open(books_path, 'r', encoding='utf-8') as f:
        books_raw = yaml.safe_load(f)
    
    books_data = []
    author_sets = set()
    for b in books_raw:
        bid = b.get(':id')
        author_str = b.get(':author', '')
        authors = frozenset([a.strip() for a in str(author_str).split(',') if a.strip()])
        if authors:
            author_sets.add(authors)
        books_data.append({'book_id': bid, 'authors': authors})
    
    df_books = pd.DataFrame(books_data).drop_duplicates(subset=['book_id'])
    num_unique_authors = len(author_sets)
    
    # 3. Orders
    orders_path = os.path.join(folder_path, 'orders.parquet')
    df_orders = pd.read_parquet(orders_path).drop_duplicates()
    
    df_orders['unit_price_parsed'] = df_orders['unit_price'].apply(parse_price)
    df_orders['quantity'] = pd.to_numeric(df_orders['quantity'], errors='coerce').fillna(0)
    df_orders['paid_price'] = df_orders['quantity'] * df_orders['unit_price_parsed']
    
    dates_clean = df_orders['timestamp'].astype(str).str.replace(r'[;,]', ' ', regex=True).str.replace(r'\.\s*M\.', 'M', case=False, regex=True)
    df_orders['parsed_date'] = pd.to_datetime(dates_clean, format='mixed', dayfirst=False, errors='coerce')
    df_orders['date_str'] = df_orders['parsed_date'].dt.strftime('%Y-%m-%d')
    
    daily_revenue = df_orders.groupby('date_str')['paid_price'].sum().reset_index()
    top_5_days = daily_revenue.sort_values(by='paid_price', ascending=False).head(5)['date_str'].tolist()
    
    # Author popularity
    df_orders_merged = df_orders.merge(df_books, on='book_id', how='left')
    author_sales = df_orders_merged.groupby('authors')['quantity'].sum()
    if not author_sales.empty:
        top_author_tuple = author_sales.idxmax()
        top_author = list(top_author_tuple) if pd.notna(top_author_tuple) else []
    else:
        top_author = []
        
    # Top buyer
    df_orders_merged['canonical_user_id'] = df_orders_merged['user_id'].map(user_id_to_canonical)
    user_spending = df_orders_merged.groupby('canonical_user_id')['paid_price'].sum()
    if not user_spending.empty:
        best_canonical = user_spending.idxmax()
        best_buyer_ids = user_clusters.get(best_canonical, [])
        best_buyer_ids = [int(x) for x in best_buyer_ids]
    else:
        best_buyer_ids = []

    # Chart Generation
    plt.figure(figsize=(10, 5))
    daily_revenue_sorted = daily_revenue.sort_values('date_str')
    
    daily_revenue_sorted = daily_revenue_sorted.dropna(subset=['date_str'])
    plt.plot(daily_revenue_sorted['date_str'], daily_revenue_sorted['paid_price'], marker='o', linestyle='-', color='#7c3aed', linewidth=2)
    plt.title('Daily Revenue', color='#e2e8f0')
    plt.xlabel('Date', color='#94a3b8')
    plt.ylabel('Revenue ($)', color='#94a3b8')
    
   
    import matplotlib.ticker as ticker
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(10))
    plt.xticks(rotation=45, color='#94a3b8')
    plt.yticks(color='#94a3b8')
    plt.gca().set_facecolor('none')
    plt.gcf().patch.set_alpha(0)  
    
   
    for spine in plt.gca().spines.values():
        spine.set_color('#475569')

    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    plt.close()
    chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return {
        'top_5_days': top_5_days,
        'unique_users': num_unique_users,
        'unique_authors': num_unique_authors,
        'top_author': top_author,
        'best_buyer': best_buyer_ids,
        'chart': chart_base64
    }

def main():
    base_dir = 'data/data'
    folders = ['DATA1', 'DATA2', 'DATA3']
    results = {}
    for f in folders:
        path = os.path.join(base_dir, f)
        res = process_folder(path)
        results[f] = res
        
    with open('results.json', 'w') as f:
        json.dump(results, f)
    
    print("Done generating results.json")

if __name__ == '__main__':
    main()
