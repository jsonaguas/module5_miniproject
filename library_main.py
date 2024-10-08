import mysql.connector
from mysql.connector import Error

def connect_database():
    db_name = 'Library'
    user = 'root'
    password = '@3$p@2o2O'
    host = 'localhost'

    try:
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )

        print('Connected to MySQL database')
        return conn

    except Error as e:
        print(f"Error: {e}")
        return None