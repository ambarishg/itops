from abc import ABC, abstractmethod
import pandas as pd

class FileHelper(ABC):
    @abstractmethod
    def read_file(self, filename: str) -> pd.DataFrame:
        """
        Reads a file from a source and returns it as a DataFrame.
        
        Parameters:
        filename (str): The name of the file.
        
        Returns:
        pd.DataFrame: The DataFrame containing the file data.
        """
        pass

    @abstractmethod
    def get_cluster_names(self, insights_file_name: str) -> pd.Series:
        """
        Retrieves cluster names from a specified insights file and counts their occurrences.
        
        Parameters:
        insights_file_name (str): The name of the insights file.
        
        Returns:
        pd.Series: A Series containing the counts of unique cluster names.
        """
        pass