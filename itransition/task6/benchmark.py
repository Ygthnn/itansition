import psycopg2
import time

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    database="fake_users",
    user="postgres",
    password="1234"
)

cur = conn.cursor()

amount = 10000

start = time.time()

cur.execute(
    "SELECT * FROM generate_fake_users(%s, %s, %s, %s)",
    ("en_US", 123, 0, amount)
)

cur.fetchone()

end = time.time()

elapsed = end - start

print(f"Generated {amount} users in {elapsed:.2f} seconds")
print(f"Speed: {amount / elapsed:.2f} users/second")

cur.close()
conn.close()