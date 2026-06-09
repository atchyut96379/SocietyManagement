import pyodbc

from app.database.connection import build_connection_string


def get_connection():
    return pyodbc.connect(build_connection_string())
