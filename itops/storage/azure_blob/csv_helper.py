import pandas as pd
from itops.storage.azure_blob.azure_blob_helper import AzureBlobHelper


class CSVHelper:
    def __init__(
            self,
            azure_blob_helper
    ):
        self.azure_blob_helper = azure_blob_helper

    def read_csv(self,filename):
        blob_stream = self.azure_blob_helper.get_blob_stream(filename)

        df = pd.read_csv(blob_stream)
        return df
    
    def get_cluster_names(self,insights_file_name):
        blob_stream = self.azure_blob_helper.get_blob_stream(insights_file_name)

        df = pd.read_csv(blob_stream)

        return(df["CLUSTER_NAMES"].value_counts())
    
    
    