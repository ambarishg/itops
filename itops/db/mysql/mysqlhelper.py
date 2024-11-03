import mysql.connector
from mysql.connector import Error
from itops.db.databasehelper import DatabaseHelper

class MySQLHelper(DatabaseHelper):
    def __init__(self, host, user, password, database):
        self.connection = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error: {e}")

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")