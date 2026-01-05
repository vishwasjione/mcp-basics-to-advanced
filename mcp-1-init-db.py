import sqlite3
from datetime import date, timedelta

db_path = "store.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS sales")
cur.execute("DROP TABLE IF EXISTS products")

cur.execute("""
CREATE TABLE products (
  product_id INTEGER PRIMARY KEY,
  product_name TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE sales (
  sale_id INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL,
  sale_date TEXT NOT NULL,     -- ISO date: YYYY-MM-DD
  qty INTEGER NOT NULL,
  unit_price REAL NOT NULL,
  FOREIGN KEY(product_id) REFERENCES products(product_id)
)
""")

products = [
  (1, "iPhone Case"),
  (2, "USB-C Cable"),
  (3, "Wireless Mouse"),
]
cur.executemany("INSERT INTO products(product_id, product_name) VALUES (?, ?)", products)

today = date.today()
rows = [
  (1, (today - timedelta(days=10)).isoformat(), 3, 19.99),
  (2, (today - timedelta(days=3)).isoformat(), 5, 9.99),
  (3, (today - timedelta(days=1)).isoformat(), 2, 24.99),
  (2, (today).isoformat(), 1, 9.99),
]
cur.executemany(
  "INSERT INTO sales(product_id, sale_date, qty, unit_price) VALUES (?, ?, ?, ?)",
  rows
)

conn.commit()
conn.close()
print(f"Initialized {db_path}")
