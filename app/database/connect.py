import psycopg2
from psycopg2._psycopg import connection

from ..static import DATA_SOURCE


def connect():
    try:
        db_connection: connection = psycopg2.connect(
            dsn=DATA_SOURCE,
            port=5432
        )
        return db_connection

    except Exception as e:
        print(e)
