import os
import sqlite3
import pymysql
import pymysql.cursors
from flask import current_app, g

def get_db_config():
    """Extract MySQL database parameters from Flask current_app config or fallback defaults."""
    if current_app:
        return {
            'host': current_app.config.get('MYSQL_HOST', 'localhost'),
            'port': current_app.config.get('MYSQL_PORT', 3306),
            'user': current_app.config.get('MYSQL_USER', 'root'),
            'password': current_app.config.get('MYSQL_PASSWORD', ''),
            'database': current_app.config.get('MYSQL_DB', 'wellness_db'),
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': False,
            'charset': 'utf8mb4',
            'connect_timeout': 3
        }
    return {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', ''),
        'database': os.environ.get('MYSQL_DB', 'wellness_db'),
        'cursorclass': pymysql.cursors.DictCursor,
        'autocommit': False,
        'charset': 'utf8mb4',
        'connect_timeout': 3
    }

def get_sqlite_db():
    """Create SQLite connection with dictionary row factory."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'wellness.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    """
    Retrieve or create a database connection bound to the current Flask context (g).
    Auto-detects MySQL; falls back to SQLite if MySQL raises OperationalError or if DB_ENGINE=sqlite.
    """
    if 'db' not in g:
        engine = os.environ.get('DB_ENGINE', 'auto').lower()
        if engine in ('auto', 'mysql'):
            try:
                config = get_db_config()
                g.db = pymysql.connect(**config)
                g.db_type = 'mysql'
            except Exception:
                g.db = get_sqlite_db()
                g.db_type = 'sqlite'
        else:
            g.db = get_sqlite_db()
            g.db_type = 'sqlite'
    return g.db

def close_db(e=None):
    """Close the database connection if open at the end of request context."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    """
    Execute a parameterized SQL query safely across MySQL and SQLite.
    
    :param query: SQL string with %s placeholders
    :param params: tuple or list of parameters
    :param fetchone: Return single row as dict if True
    :param fetchall: Return list of dict rows if True
    :param commit: Perform transaction commit if True
    :return: Query result, inserted row ID, or affected row count
    """
    conn = get_db()
    db_type = getattr(g, 'db_type', 'mysql')
    
    if db_type == 'sqlite':
        sql = query.replace('%s', '?')
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if commit:
                conn.commit()
                res = cursor.lastrowid if cursor.lastrowid else cursor.rowcount
                cursor.close()
                return res
            if fetchone:
                row = cursor.fetchone()
                cursor.close()
                return dict(row) if row else None
            if fetchall:
                rows = cursor.fetchall()
                cursor.close()
                return [dict(r) for r in rows]
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
        except Exception as err:
            if commit:
                conn.rollback()
            raise err
    else:
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
