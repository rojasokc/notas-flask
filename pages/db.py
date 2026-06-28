import os
import mysql.connector

def get_db_connection():

    host = os.getenv("DB_HOST", "localhost")

    return mysql.connector.connect(
        host=host,
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Tucodata1!"),
        database=os.getenv("DB_NAME", "tucodata")
    )