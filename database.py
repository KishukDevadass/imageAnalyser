import sqlite3
from datetime import datetime

DB_NAME = "history.db"

def init_db():
    """Creates the table if it doesn't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                prompt TEXT,
                result TEXT
            )
        ''')
        conn.commit()

def save_analysis(prompt, result):
    """Saves a new analysis record."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "INSERT INTO analysis_history (timestamp, prompt, result) VALUES (?, ?, ?)",
            (timestamp, prompt, result)
        )
        conn.commit()

def get_all_history():
    """Retrieves all records from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM analysis_history ORDER BY id DESC")
        return c.fetchall()