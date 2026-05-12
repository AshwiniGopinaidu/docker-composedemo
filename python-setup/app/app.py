import time
import psycopg2
from flask import Flask
import os

app = Flask(__name__)

# Connection settings from environment variables (best practice)
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "testdb")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")

def get_db_connection():
    """Retries connection until Postgres is ready."""
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            return conn
        except psycopg2.OperationalError:
            print("Postgres is unavailable, waiting...")
            time.sleep(2)

def init_db():
    """Creates the visits table if it doesn't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS counters (id serial PRIMARY KEY, visits integer);')
    cur.execute('INSERT INTO counters (id, visits) VALUES (1, 0) ON CONFLICT DO NOTHING;')
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    # Increment the counter in Postgres
    cur.execute('UPDATE counters SET visits = visits + 1 WHERE id = 1 RETURNING visits;')
    count = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return f"Hello! You have visited {count} times 🚀"

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
