import pandas as pd
import numpy as np

df = pd.read_csv('data/data/DATA3/users.csv')
print("Total rows:", len(df))
df = df.fillna('')
records = df[['name', 'address', 'phone', 'email']].to_dict('records')

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
    for j in range(i + 1, n):
        r1 = records[i]
        r2 = records[j]
        matches = 0
        if r1['name'] != '' and r1['name'] == r2['name']: matches += 1
        if r1['address'] != '' and r1['address'] == r2['address']: matches += 1
        if r1['phone'] != '' and r1['phone'] == r2['phone']: matches += 1
        if r1['email'] != '' and r1['email'] == r2['email']: matches += 1
        pass

# match if sum((r1[k] == r2[k])) >= 3
for i in range(n):
    for j in range(i + 1, n):
        r1 = records[i]
        r2 = records[j]
        matches = sum(1 for k in ['name', 'address', 'phone', 'email'] if r1[k] == r2[k] and r1[k] != '')
        if matches >= 3:
            union(i, j)


parent = list(range(n))

def find2(i):
    if parent[i] == i:
        return i
    parent[i] = find2(parent[i])
    return parent[i]

def union2(i, j):
    root_i = find2(i)
    root_j = find2(j)
    if root_i != root_j:
        parent[root_i] = root_j

edge_count = 0
for i in range(n):
    for j in range(i + 1, n):
        r1 = records[i]
        r2 = records[j]

        matches = sum(1 for k in ['name', 'address', 'phone', 'email'] if r1[k] == r2[k])
        if matches >= 3:
            union2(i, j)
            edge_count += 1

components = set(find2(i) for i in range(n))
print("Edges:", edge_count)
print("Unique users (components):", len(components))

