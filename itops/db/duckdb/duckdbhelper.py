import duckdb
from abc import ABC, abstractmethod
from itops.db.databasehelper import DatabaseHelper

class DuckDBDatabaseHelper(DatabaseHelper):
    def __init__(self, database_file):
        self.database_file = database_file
        self.connection = None

    def connect(self):
        """Establish a connection to the DuckDB database."""
        self.connection = duckdb.connect(self.database_file)
        print(f"Connected to DuckDB database: {self.database_file}")

    def execute_query(self, query, params=None):
        """Execute a single query (INSERT, UPDATE, DELETE)."""
        self.connection.execute(query, params or ())
        print("Query executed successfully.")

    def fetch_all(self, query, params=None):
        """Fetch all results from a SELECT query."""
        results = self.connection.execute(query, params or ()).fetchall()
        print(f"Fetched {len(results)} rows.")
        return results

    def fetch_one(self, query, params=None):
        """Fetch a single result from a SELECT query."""
        result = self.connection.execute(query, params or ()).fetchone()
        print("Fetched one row." if result else "No rows found.")
        return result

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Connection closed.")

