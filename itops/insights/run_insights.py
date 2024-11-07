from itops.storage.azure_blob.azure_blob_helper import AzureBlobHelper
from itops.storage.azure_blob.parquet_helper import ParquetHelper
import pandas as pd
import numpy as np

from itops.db.mysql.mysqlhelper import MySQLHelper
from itops.db.duckdb.duckdbhelper import DuckDBDatabaseHelper
from itops.db.sqlite.sqlitehelper import SQLiteDatabaseHelper

from itops.llm.azureopenaimanager.azure_open_ai_helper import AzureOpenAIManager
from itops.config.configs import CONFIGS
import os

from pprint import pprint

class InsightsManager:

    CHUNK_SIZE = 5000

    def __init__(self,db_type ="SQLITE"):
        self.db_type = db_type
    
        if self.db_type == "DUCKDB":
            self.db_helper = DuckDBDatabaseHelper("itops.duckdb")
        elif self.db_type == "MYSQL":
            self.db_helper = MySQLHelper(CONFIGS.HOST,
                           CONFIGS.USERNAME_MYSQL,
                           CONFIGS.PASSWORD, "itops")
        elif self.db_type =="SQLITE":
            self.db_helper = SQLiteDatabaseHelper("itops.db")
        
    
        
        self.azure_open_ai_helper = AzureOpenAIManager(endpoint=CONFIGS.AZURE_OPENAI_ENDPOINT,
                                          api_key =CONFIGS.AZURE_OPENAI_API_KEY,
                                          deployment_id=CONFIGS.AZURE_OPENAI_DEPLOYMENT_ID,
                                      api_version = "2024-02-01")
        
     
        
  
    def get_input_filename(self,
                           run_name,
                           cluster_name):
        
        # Fetch and display all records to verify insertion
        select_query = 'SELECT \
            INSIGHTS_FILE_NAME \
            FROM cluster_data \
            WHERE RUN_NAME = %s \
            AND CLUSTER_NAME = %s'
        
        select_query = self.query_helper(select_query)

        print(select_query)

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,
                [run_name,cluster_name])
        self.db_helper.close_connection()

        if len(records) == 0:
            return None
        if records is None:
            return records
        
        azure_blob_helper01 = AzureBlobHelper(CONFIGS.AZURE_BLOB_STORAGE_ACCOUNT,
                                              CONFIGS.AZURE_BLOB_STORAGE_KEY,
                                   CONFIGS.AZURE_BLOB_STORAGE_CONTAINER)
        
        file_helper01 = self.get_file_helper(azure_blob_helper01)

        df = file_helper01.read_file(records[0][0]
                                   )
       
        return df
    
    def get_all_text(self,
                     data,
                     description_column_name):
        text_all = ''

        for index,row in data.iterrows():
            if index == 0:
                text_all = str(row[description_column_name])
            else:
                text_all = text_all + " \n " + str(row[description_column_name])

        return(text_all)


    def chunk_text(self,text,chunk_size=CHUNK_SIZE ):
        chunks = []

        for i in range(0,len(text),chunk_size):
            chunk = text[i:i+chunk_size]
            chunks.append(chunk)
        
        return(chunks)

    def get_consolidated_response(self,
                                  text,
                                  user_input):
        reply_all = ""

        if text is None:
            return reply_all
        
        chunk_list = self.chunk_text(text)
        for chunk in chunk_list:
            reply = self.azure_open_ai_helper.generate_reply_from_context(user_input, 
                                                                    chunk, 
                                                                    conversation=[])
            reply_all = reply_all + " " + reply[0]
        
        if (len(chunk_list) > 1):
            reply_2 = self.azure_open_ai_helper.generate_reply_from_context(user_input, 
                                                                    chunk, 
                                                                    conversation=[])
        else:
            reply_2 = reply_all

        return(reply_2)

    def get_insights_specific_attr(self,run_name,cluster_name,
                     description_column_name,
                     prompt):

        df = self.get_input_filename(
            run_name,cluster_name
        )

        if df is None:
            return None

        text_all = self.get_all_text(df,
                            description_column_name)

       
        reply = self.get_consolidated_response(
            text = text_all,
            user_input = prompt
        )

        return reply

    def query_helper(self,query):

        if self.db_type == "DUCKDB" or self.db_type == "SQLITE":
            query = query.replace('%s', '?')
        
        return(query)
    
    def get_file_helper(self, azure_blob_helper01):
        file_helper01 = ParquetHelper(azure_blob_helper01)
        return file_helper01

    def get_cluster_counts(self,run_name,cluster_name):
         
         df = self.get_input_filename(
            run_name,cluster_name
         )
         
         return (df["CLUSTER_NAMES"].value_counts())