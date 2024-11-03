from abc import ABC, abstractmethod

class DatabaseHelper(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute_query(self, query, params=None):
        pass

    @abstractmethod
    def fetch_all(self, query, params=None):
        pass

    @abstractmethod
    def fetch_one(self, query, params=None):
        pass

    @abstractmethod
    def close_connection(self):
        pass