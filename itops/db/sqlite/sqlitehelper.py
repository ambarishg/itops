import sqlite3
from itops.db.databasehelper import DatabaseHelper

class SQLiteDatabaseHelper(DatabaseHelper):
    def __init__(self, database_file):
        self.database_file = database_file
        self.connection = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.connection = sqlite3.connect(self.database_file)
        print(f"Connected to database: {self.database_file}")

    def execute_query(self, query, params=None):
        """Execute a single query (INSERT, UPDATE, DELETE)."""
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        self.connection.commit()
        print("Query executed successfully.")

    def fetch_all(self, query, params=None):
        """Fetch all results from a SELECT query."""
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        print(f"Fetched {len(results)} rows.")
        return results

    def fetch_one(self, query, params=None):
        """Fetch a single result from a SELECT query."""
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        print("Fetched one row." if result else "No rows found.")
        return result

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Connection closed.")