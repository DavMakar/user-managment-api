import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv('DATABASE_URL')

def create_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def query_db(query, args=(), one=False, commit=False):
    conn = create_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, args)
        
        if commit:
            conn.commit()
        
        if "SELECT" in query.upper():
            rv = cur.fetchone() if one else cur.fetchall()
        else:
            rv = cur.rowcount
        
        cur.close()
        return rv
    except Exception as e:
        conn.rollback()
        raise Exception(f"Database error: {str(e)}")
    finally:
        conn.close()