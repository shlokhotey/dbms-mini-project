import os
import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "dbname":   os.getenv("DB_NAME",     "retail_chain"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", "patthar"),
    "port":     os.getenv("DB_PORT",     "5433"),
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute("SELECT * FROM sales")
print(cur.fetchall())

cur.close()
conn.close()