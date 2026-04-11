import yaml

with open('data/data/DATA1/books.yaml', 'r') as f:
    books = yaml.safe_load(f)

print(list(books[0].keys()))

author_sets = set()
for b in books:
    author_str = b.get(':author', '')
    if not author_str:
        continue
    authors = frozenset([a.strip() for a in author_str.split(',') if a.strip()])
    author_sets.add(authors)
print("Unique sets:", len(author_sets))
