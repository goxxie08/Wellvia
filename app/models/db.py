import pymysql
import pymysql.cursors
from flask import current_app, g

def get_db_config():
    """Extract database parameters from Flask current_app config or fallback defaults."""
    if current_app:
        return {
            'host': current_app.config.get('MYSQL_HOST', 'localhost'),
            'port': current_app.config.get('MYSQL_PORT', 3306),
            'user': current_app.config.get('MYSQL_USER', 'root'),
            'password': current_app.config.get('MYSQL_PASSWORD', ''),
            'database': current_app.config.get('MYSQL_DB', 'wellness_db'),
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': False,
            'charset': 'utf8mb4'
        }
    return {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',
        'database': 'wellness_db',
        'cursorclass': pymysql.cursors.DictCursor,
        'autocommit': False,
        'charset': 'utf8mb4'
    }

def get_db():
    """Retrieve or create a database connection bound to the current Flask application context (g)."""
    if 'db' not in g:
        config = get_db_config()
        g.db = pymysql.connect(**config)
    return g.db

def close_db(e=None):
    """Close the database connection if open at the end of request context."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    """
    Execute a parameterized SQL query safely.
    
    :param query: SQL string with %s placeholders
    :param params: tuple or list of parameters
    :param fetchone: Return single row as dict if True
    :param fetchall: Return list of dict rows if True
    :param commit: Perform transaction commit if True
    :return: Query result, inserted row ID, or affected row count
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if commit:
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            return cursor.rowcount
    except Exception as err:
        if commit:
            conn.rollback()
        raise err
