import psycopg2
import psycopg2.extras
import os

def db_connection():
    conn = psycopg2.connect(host="localhost",
                            database="SUPJournal",
                            user=os.environ["DB_USERNAME"],
                            password=os.environ["DB_PASSWORD"])
    return conn

def db_query(query, arguments:tuple=None, insert=False, get=False):
    data = None
    db = db_connection()
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as db_cur:
        if insert:
            db_cur.execute(query, arguments)
            db.commit()
        elif get:
            db_cur.execute(query, arguments)
            data = db_cur.fetchone()
    db.close()
    if data:
        return data

