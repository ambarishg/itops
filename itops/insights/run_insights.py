from itops.storage.azure_blob.azure_blob_helper import AzureBlobHelper
from itops.storage.azure_blob.parquet_helper import ParquetHelper
import pandas as pd

class InsightsManager:

    CHUNK_SIZE = 5000

    def __init__(self,
                 db_helper,
                 llm_helper,
                 azure_blob_account,
                 azure_blob_container,
                 azure_storage_key,
                 db_type ="SQLITE",):
        self.db_type = db_type
    
        self.db_helper = db_helper
        self.azure_open_ai_helper = llm_helper
        self.azure_blob_account = azure_blob_account
        self.azure_blob_container = azure_blob_container
        self.azure_storage_key = azure_storage_key
        
    def get_input_filename(self,
                           run_name,
                           category_name,
                           cluster_name = None):
        
        if cluster_name:
            select_query = 'SELECT \
            INSIGHTS_FILE_NAME,CLUSTER_ID,CLUSTER_NAME \
            FROM cluster_data \
            WHERE RUN_ID = %s \
            AND CATEGORY = %s \
            AND CLUSTER_ID = %s'
        else:
            select_query = 'SELECT \
            INSIGHTS_FILE_NAME,CLUSTER_ID,CLUSTER_NAME \
            FROM cluster_data \
            WHERE RUN_ID = %s \
            AND CATEGORY = %s '
        
        select_query = self.query_helper(select_query)

        print(select_query)

        self.db_helper.connect()

        if cluster_name:
            records = self.db_helper.fetch_all(select_query,
                [run_name,category_name,cluster_name])
        else:
             records = self.db_helper.fetch_all(select_query,
                [run_name,category_name])
             
        self.db_helper.close_connection()

        if len(records) == 0:
            return None
        if records is None:
            return records
        
        df_records = pd.DataFrame(records,
                                  columns = ["INSIGHTS_FILE_NAME",
                                             "CLUSTER_ID",
                                             "CLUSTER_NAMES"])
        
        azure_blob_helper01 = AzureBlobHelper(account_name=self.azure_blob_account,
                                              account_key=self.azure_storage_key,
                                   container_name=self.azure_blob_container)
        
        file_helper01 = self.get_file_helper(azure_blob_helper01)

        print(records[0][0])
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
                                                                    reply_all, 
                                                                    conversation=[])
            reply_all = reply_2[0]

        return(reply_all)

    def get_insights_specific_attr(self,run_name,category_name,cluster_name,
                     description_column_name,
                     prompt):

        df = self.get_input_filename(
            run_name,category_name,cluster_name
        )

        if df is None:
            return None
        
        print(df.columns)
        print(cluster_name)
        
        df = df[df["CLUSTER_ID"] == cluster_name ]

        

        input_file_name, \
        description_column_name_ticket, \
            challenge_col, \
                solution_col = self.get_category_data(category_name=category_name)
        
        print(input_file_name, \
        description_column_name_ticket, \
            challenge_col, \
                solution_col)
        
        if challenge_col is None:
            challenge_col = ""
        if solution_col is None:
            solution_col = ""

        if description_column_name == "Challenge":
            if (challenge_col == "" ):
                return ""
            
            text_all = self.get_all_text(df,
                                challenge_col)
        elif description_column_name == "Solution":
            if (solution_col == "" ):
                return ""
            text_all = self.get_all_text(df,
                                solution_col)

       
        reply = self.get_consolidated_response(
            text = text_all,
            user_input = prompt
        )

        print(reply)

        return reply

    def query_helper(self,query):

        if self.db_type == "DUCKDB" or self.db_type == "SQLITE":
            query = query.replace('%s', '?')
        
        return(query)
    
    def get_file_helper(self, azure_blob_helper01):
        file_helper01 = ParquetHelper(azure_blob_helper01)
        return file_helper01

    def get_cluster_counts(self,run_name,category_name,cluster_name):
         
         df = self.get_input_filename(
            run_name,category_name,cluster_name
         )
         
         df_counts = df.groupby(by=["CLUSTER_ID","CLUSTER_NAMES"])["CLUSTERS"].count()

        # Output is of the form
        #   [
        #   {
        #     "CLUSTER_ID": "1a861341-1559-4b69-903e-6d5a88e1f377",
        #     "CLUSTER_NAMES": "IT support and software issues.",
        #     "CLUSTERS": 16
        #   },
        #   {
        #     "CLUSTER_ID": "4de7029f-e042-482b-b9af-fe97501a9038",
        #     "CLUSTER_NAMES": "Device requests and technical issues.",
        #     "CLUSTERS": 19
        #   }, ]
         return (df_counts)
    
    def get_category_data(self,category_name):
        select_query = """
              SELECT INPUT_FILE_NAME , 
                    DESCRIPTION_COL , 
                    CHALLENGE_COL , 
                    SOLUTION_COL  
              FROM 
              category_data
              WHERE CATEGORY = %s 
              """
        
        select_query = self.query_helper(select_query)

        print(select_query)
        category_to_search = category_name

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,[category_to_search])
        self.db_helper.close_connection()

        if records:
            return(records[0][0],
                   records[0][1],
                   records[0][2],
                   records[0][3],
                   )
