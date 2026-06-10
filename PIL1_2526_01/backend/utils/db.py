import mysql.connector
from mysql.connector import Error
from flask import current_app, g


def get_db():
    """Retourne une connexion à la base de données."""
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB'],
                charset='utf8mb4'
            )
        except Error as e:
            current_app.logger.error(f"Erreur connexion DB: {e}")
            raise e
    return g.db


def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """Exécute une requête SQL et retourne les résultats."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if commit:
            db.commit()
            return cursor.lastrowid
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        return cursor
    except Error as e:
        db.rollback()
        current_app.logger.error(f"Erreur SQL: {e} | SQL: {sql}")
        raise e
    finally:
        cursor.close()


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()
