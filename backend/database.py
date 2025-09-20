import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection - PostgreSQL only"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise Exception("DATABASE_URL environment variable is required. Please set it to your PostgreSQL connection string.")
    
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def init_db():
    """Initialize database tables - PostgreSQL only"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # PostgreSQL schema
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        UNIQUE(user_id, name)
    )""")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tests (
        id SERIAL PRIMARY KEY,
        subject_id INTEGER,
        name VARCHAR(255) NOT NULL,
        FOREIGN KEY(subject_id) REFERENCES subjects(id),
        UNIQUE(subject_id, name)
    )""")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        id SERIAL PRIMARY KEY,
        test_id INTEGER,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        mastered BOOLEAN DEFAULT FALSE,
        FOREIGN KEY(test_id) REFERENCES tests(id)
    )""")
    
    conn.commit()
    conn.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """Execute a query and return results"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        else:
            result = cur.rowcount
            
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def insert_subject(name, user_id):
    """Insert a subject and return its ID"""
    query = "INSERT INTO subjects (name, user_id) VALUES (%s, %s) ON CONFLICT (user_id, name) DO NOTHING"
    execute_query(query, (name, user_id), fetch_all=False)
    
    # Get the ID
    query = "SELECT id FROM subjects WHERE name = %s AND user_id = %s"
    result = execute_query(query, (name, user_id), fetch_one=True)
    return result['id'] if result else None

def insert_test(name, subject_id):
    """Insert a test and return its ID"""
    query = "INSERT INTO tests (name, subject_id) VALUES (%s, %s) ON CONFLICT (subject_id, name) DO NOTHING"
    execute_query(query, (name, subject_id), fetch_all=False)
    
    # Get the ID
    query = "SELECT id FROM tests WHERE name = %s AND subject_id = %s"
    result = execute_query(query, (name, subject_id), fetch_one=True)
    return result['id'] if result else None

def get_existing_flashcard_fronts(test_id):
    """Get existing flashcard front texts for a test"""
    query = "SELECT front FROM flashcards WHERE test_id = %s"
    results = execute_query(query, (test_id,))
    return set(row['front'] for row in results)

def insert_flashcards(test_id, flashcards):
    """Insert flashcards for a test"""
    if not flashcards:
        return
    
    query = "INSERT INTO flashcards (test_id, front, back) VALUES (%s, %s, %s)"
    params = [(test_id, front, back) for front, back in flashcards]
    
    cur = None
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.executemany(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()
