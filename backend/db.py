# db.py
import sqlite3

def init_db():
    conn = sqlite3.connect("study.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY(subject_id) REFERENCES subjects(id),
        UNIQUE(subject_id, name)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        mastered BOOLEAN DEFAULT 0,
        FOREIGN KEY(test_id) REFERENCES tests(id)
    )""")

    conn.commit()
    conn.close()
