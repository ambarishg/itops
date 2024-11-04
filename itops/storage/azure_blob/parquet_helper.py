import pandas as pd
from itops.storage.azure_blob.azure_blob_helper import AzureBlobHelper
from itops.storage.azure_blob.file_helper import FileHelper
from typing import Optional
import io

class ParquetHelper(FileHelper):
    
    def __init__(self, azure_blob_helper: AzureBlobHelper):
        self.azure_blob_helper = azure_blob_helper

    def read_file(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Reads a Parquet file from Azure Blob Storage and returns it as a DataFrame.

        Parameters:
        filename (str): The name of the Parquet file in Azure Blob Storage.

        Returns:
        pd.DataFrame: The DataFrame containing the Parquet data or None if an error occurs.
        """
        try:
            stream = io.BytesIO()
            blob_stream = self.azure_blob_helper.get_blob_stream(filename)
            blob_stream.readinto(stream)

            # Move the stream pointer to the beginning
            stream.seek(0)
            df = pd.read_parquet(stream)  # Using Pandas to read Parquet
            return df
        except Exception as e:
            print(f"Error reading Parquet file {filename}: {e}")
            return None
    
    def get_cluster_names(self, insights_file_name: str) -> pd.Series:
        """
        Retrieves cluster names from a specified insights file and counts their occurrences.

        Parameters:
        insights_file_name (str): The name of the insights Parquet file in Azure Blob Storage.

        Returns:
        pd.Series: A Series containing the counts of unique cluster names.
        """
        try:
            df = self.read_file(insights_file_name)
            return df["CLUSTER_NAMES"].value_counts()
        
        except Exception as e:
            print(f"Error reading insights Parquet file {insights_file_name}: {e}")
            return pd.Series()
