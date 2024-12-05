from itops.storage.azure_blob.azure_blob_helper import AzureBlobHelper
from itops.storage.azure_blob.csv_helper import CSVHelper
from itops.storage.azure_blob.parquet_helper import ParquetHelper
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import pandas as pd


from itops.embeddings.embedding_generator import EmbeddingGenerator
import os

class RunManager:

    def __init__(self,
                 description_column_name,
                 embedding_model_name,
                 azure_open_ai_helper,
                 azure_blob_account,
                 azure_blob_container,
                 azure_storage_key,
                 db_helper,
                 db_type = "MYSQL",
                 ):
        
        self.db_type = db_type

  

        self.set_storage_helpers(azure_blob_account, 
                                 azure_blob_container, 
                                 azure_storage_key)

        self.azure_open_ai_helper= azure_open_ai_helper
        self.db_helper = db_helper
        self.description_column_name = description_column_name
        self.embedding_model_name = embedding_model_name
        self.generator = EmbeddingGenerator(self.embedding_model_name)

    def set_storage_helpers(self, 
                            azure_blob_account, 
                            azure_blob_container, 
                            azure_storage_key):
        
        self.azure_blob_account =azure_blob_account   
        self.azure_blob_container = azure_blob_container
        self.azure_blob_storage_key = azure_storage_key
        
        self.azure_blob_helper = AzureBlobHelper(self.azure_blob_account,
                                                      self.azure_blob_storage_key,
                                                      self.azure_blob_container)
     
        self.csv_helper = CSVHelper(self.azure_blob_helper)

    def get_embedding_query_vector(self,query,model_name):
        """Get the vector of the query

        Args:
            query (string): user input

        Returns:
            _type_: vector of the query
        """
        model = SentenceTransformer(model_name)
        query_vector = model.encode(query)
        return query_vector
        
    def generate_themes_and_embeddings(self,filename,
                                       user_input):

        """_summary_

        Returns:
            1. Themes
            2. Embeddings in the NEW Dataset
        """

        df = self.csv_helper.read_file(filename)

        reply_list = []
        
        for i in range(len(df)):
            content = df.iloc[i][self.description_column_name]
            content = str(content)
            reply = self.azure_open_ai_helper.generate_reply_from_context(user_input, 
                                                                    content, 
                                                                    conversation=[])
            reply_list.append(reply[0])
            reply =""
            print(f"Completed THEMES {i+1} ROW")

        df["themes"] = reply_list

        df_new =self.generate_embedding_dataset(df)

        return df_new

    def generate_embedding_dataset(self, df):
        df_with_embeddings = self.generator.generate_embedding_dataset(df)
        return df_with_embeddings
    
    def generate_clusters(self,
                          df,
                          num_clusters,
                          user_input
                          ):
        
        kmeans = KMeans(n_clusters=num_clusters, random_state=0)
        embedding_array = (df["embeddings"].tolist())
        kmeans.fit(embedding_array)
        labels = kmeans.labels_
        df["CLUSTERS"] = labels

        cluster_name_list = []
        for i in range(num_clusters):
            df_cluster = df[df["CLUSTERS"] == i]
            full_content = ""
            for j in range(len(df_cluster)):
                content = df_cluster.iloc[j][self.description_column_name]
                full_content = full_content + str(content) + " \n "
            
            cluster_name = self.azure_open_ai_helper.generate_reply_from_context(user_input, 
                                                                    full_content, 
                                                                    conversation=[])
            cluster_name_list.append(cluster_name[0])
            cluster_name =""
            print(f"Completed CLUSTERING PART 1 {i+1} ROW")

        cluster_number_list= []
        cluster_id_list = []
        for i in range(len(cluster_name_list)):
            cluster_number_list.append(i)
            cluster_id_list.append(self.get_guid())
        df_clusters = pd.DataFrame()
        df_clusters["CLUSTERS"] = cluster_number_list
        df_clusters["CLUSTER_NAMES"] = cluster_name_list
        df_clusters["CLUSTER_ID"] = cluster_id_list

        df_all = df.merge(df_clusters,)
        print(f"Completed CLUSTERING FINAL")
        return df_all

    def run_cluster(self,
                    run_name,
                    category_name,
                    input_file_name,
                    prompt,
                    num_clusters):
        
        df =  self.generate_themes_and_embeddings(input_file_name,prompt)
        df_clusters = self.generate_clusters(df,num_clusters,user_input=prompt)

        file_name_insights = input_file_name.split(".")[0] + \
            "-"+ \
                run_name + \
                      "-"+ category_name +  \
                        ".parquet"
        
        df_clusters.to_parquet(file_name_insights,index = False)

        cluster_ids = df_clusters['CLUSTER_ID'].unique()


        self.azure_blob_helper.upload_blob_from_path(file_name_insights,file_name_insights)

        os.remove(file_name_insights)

        NUMBER_OF_CLUSTERS = num_clusters
        CATEGORY = category_name
        INPUT_FILE_NAME = input_file_name
        INSIGHTS_FILE_NAME = file_name_insights
        PARENT_CLUSTER_NAME = None
        NUMBER_OF_SUBCLUSTERS = None
        RUN_ID =  self.get_guid()

        self.insert_run_log(RUN_ID,
                            run_name, 
                            NUMBER_OF_CLUSTERS, 
                            CATEGORY, 
                            INPUT_FILE_NAME, 
                            INSIGHTS_FILE_NAME, 
                            PARENT_CLUSTER_NAME,
                            NUMBER_OF_SUBCLUSTERS)
        
        for cluster_id in cluster_ids:
            CLUSTER_ID = cluster_id
            cluster_name = df_clusters[df_clusters["CLUSTER_ID"] == CLUSTER_ID]["CLUSTER_NAMES"].iloc[0]
            PARENT_CLUSTER_ID = None
            self.insert_cluster_data(
                RUN_ID = RUN_ID,
                RUN_NAME=run_name,
                CATEGORY=CATEGORY,
                INPUT_FILE_NAME=INPUT_FILE_NAME,
                INSIGHTS_FILE_NAME=INSIGHTS_FILE_NAME,
                CLUSTER_ID = CLUSTER_ID,
                CLUSTER_NAME= cluster_name,
                PARENT_CLUSTER_ID = PARENT_CLUSTER_ID,
                PARENT_CLUSTER_NAME=None)

    
    def get_input_filename_for_rerun_subcluster(self,category_name,parent_run_name):
        # Fetch and display all records to verify insertion
       
        print(f"Category Name : {category_name}")
        print(f"parent_run_name : {parent_run_name}")
        
        select_query = """
        SELECT INSIGHTS_FILE_NAME,
        CONTAINER_NAME,
        ACCOUNT_NAME 
        FROM run_log WHERE CATEGORY = %s \
        AND RUN_ID = %s 
        """
        
        select_query = self.query_helper(select_query)

        print(select_query)
        category_to_search = category_name

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,[category_to_search,parent_run_name])
        self.db_helper.close_connection()
        azure_blob_helper01 = AzureBlobHelper(records[0][2],
                                              self.azure_blob_storage_key,
                                    records[0][1])
        
        file_helper01 = self.get_file_helper(azure_blob_helper01)

        df = file_helper01.read_file(records[0][0]
                                   )
        
        return df,records[0][0]
    

    def get_input_filename_for_rerun(self,category_name):
        # Fetch and display all records to verify insertion
        select_query = 'SELECT INSIGHTS_FILE_NAME,CONTAINER_NAME,ACCOUNT_NAME FROM run_log WHERE CATEGORY = %s \
            AND PARENT_CLUSTER_NAME IS NULL '
        
        select_query = self.query_helper(select_query)

        print(select_query)
        category_to_search = category_name

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,[category_to_search])
        self.db_helper.close_connection()


        if (len(records) == 0):
            return None , None
        azure_blob_helper01 = AzureBlobHelper(records[0][2],
                                              self.azure_blob_storage_key,
                                    records[0][1])
        
        file_helper01 = self.get_file_helper(azure_blob_helper01)

        df = file_helper01.read_file(records[0][0]
                                   )
        
        return df,records[0][0]

    def get_file_helper(self, azure_blob_helper01):
        file_helper01 = ParquetHelper(azure_blob_helper01)
        return file_helper01
    
   
    
    def rerun_cluster(self,
                    run_name,
                    category_name,
                    prompt,
                    num_clusters):
        
        df,input_file_name = self.get_input_filename_for_rerun(category_name)

        if df is None:
            print("No Valid Entries for RERUN")
            return
        
        df_dropped = df
        df_dropped = df_dropped.drop('CLUSTERS', axis=1)
        df_dropped = df_dropped.drop('CLUSTER_NAMES', axis=1)
        df_dropped = df_dropped.drop('CLUSTER_ID', axis=1)

        df = df_dropped

        df_clusters = self.generate_clusters(df,num_clusters,user_input=prompt)

        cluster_ids = df_clusters['CLUSTER_ID'].unique()
        
        file_name_insights = input_file_name.split(".")[0] + \
            "-"+ \
                run_name + \
                        ".parquet" 
                
        df_clusters.to_parquet(file_name_insights,index = False)

        self.azure_blob_helper.upload_blob_from_path(file_name_insights,file_name_insights)

        os.remove(file_name_insights)

        NUMBER_OF_CLUSTERS = num_clusters
        CATEGORY = category_name
        INPUT_FILE_NAME = input_file_name
        INSIGHTS_FILE_NAME = file_name_insights
        PARENT_CLUSTER_NAME = None
        NUMBER_OF_SUBCLUSTERS = None
        RUN_ID =  self.get_guid()

        self.insert_run_log(RUN_ID,
                            run_name, 
                            NUMBER_OF_CLUSTERS, 
                            CATEGORY, 
                            INPUT_FILE_NAME, 
                            INSIGHTS_FILE_NAME, 
                            PARENT_CLUSTER_NAME,
                            NUMBER_OF_SUBCLUSTERS)
        
        for cluster_id in cluster_ids:
            CLUSTER_ID = cluster_id
            cluster_name = df_clusters[df_clusters["CLUSTER_ID"] == CLUSTER_ID]["CLUSTER_NAMES"].iloc[0]
            PARENT_CLUSTER_ID = None
            self.insert_cluster_data(
                RUN_ID = RUN_ID,
                RUN_NAME=run_name,
                CATEGORY=CATEGORY,
                INPUT_FILE_NAME=INPUT_FILE_NAME,
                INSIGHTS_FILE_NAME=INSIGHTS_FILE_NAME,
                CLUSTER_ID = CLUSTER_ID,
                CLUSTER_NAME= cluster_name,
                PARENT_CLUSTER_ID = PARENT_CLUSTER_ID,
                PARENT_CLUSTER_NAME=None)

        


    def rerun_sub_cluster(self,
                    run_name,
                    category_name,
                    prompt,
                    num_clusters,
                    parent_cluster_name,
                    parent_run_name):
        
        df,input_file_name = self.get_input_filename_for_rerun_subcluster(category_name,
                                                                          parent_run_name)
        if df is None:
            print("No Valid Entries for RERUN SUBCLUSTER")
            return
        
        
        # Get the PARENT_CLUSTER_ID and PARENT_CLUSTER_NAME
        df_parent_cluster = df[df["CLUSTER_ID"] == parent_cluster_name]
        PARENT_CLUSTER_NAME = df_parent_cluster["CLUSTER_NAMES"].iloc[0]
        PARENT_CLUSTER_ID = df_parent_cluster["CLUSTER_ID"].iloc[0]
        

        df_dropped = df_parent_cluster
        df_dropped = df_dropped.drop('CLUSTERS', axis=1)
        df_dropped = df_dropped.drop('CLUSTER_ID', axis=1)
        df_dropped = df_dropped.drop('CLUSTER_NAMES', axis=1)
 
        df = df_dropped

        df_clusters = self.generate_clusters(df,num_clusters,user_input=prompt)


        cluster_ids = df_clusters['CLUSTER_ID'].unique()

        file_name_insights = input_file_name.split(".")[0] + \
            "-"+ \
                run_name + \
                        ".parquet"
        
        df_clusters.to_parquet(file_name_insights,index = False)

        self.azure_blob_helper.upload_blob_from_path(file_name_insights,file_name_insights)

        os.remove(file_name_insights)

        NUMBER_OF_CLUSTERS = None
        CATEGORY = category_name
        INPUT_FILE_NAME = input_file_name
        INSIGHTS_FILE_NAME = file_name_insights
        NUMBER_OF_SUBCLUSTERS = num_clusters
        RUN_ID =  self.get_guid()

        self.insert_run_log(RUN_ID,run_name, 
                            NUMBER_OF_CLUSTERS, 
                            CATEGORY, 
                            INPUT_FILE_NAME, 
                            INSIGHTS_FILE_NAME, 
                            PARENT_CLUSTER_NAME,
                            NUMBER_OF_SUBCLUSTERS)
        
        for cluster_id in cluster_ids:
            CLUSTER_ID = cluster_id
            cluster_name = df_clusters[df_clusters["CLUSTER_ID"] == CLUSTER_ID]["CLUSTER_NAMES"].iloc[0]

                        #  RUN_ID,RUN_NAME, 
                        #  CATEGORY, 
                        #  INPUT_FILE_NAME, 
                        #  INSIGHTS_FILE_NAME,
                        #  CLUSTER_ID, 
                        #  CLUSTER_NAME, 
                        #  PARENT_CLUSTER_ID,
                        #  PARENT_CLUSTER_NAME

            self.insert_cluster_data(RUN_ID = RUN_ID,
                                     RUN_NAME=run_name,
                                     CATEGORY=CATEGORY,
                                     INPUT_FILE_NAME=INPUT_FILE_NAME,
                                     INSIGHTS_FILE_NAME=INSIGHTS_FILE_NAME,
                                     CLUSTER_NAME= cluster_name,
                                     PARENT_CLUSTER_NAME=PARENT_CLUSTER_NAME,
                                     CLUSTER_ID = CLUSTER_ID,
                                     PARENT_CLUSTER_ID = PARENT_CLUSTER_ID)
        return RUN_ID    

    def insert_run_log(self, 
                       RUN_ID,
                       run_name, 
                       NUMBER_OF_CLUSTERS,
                        CATEGORY, 
                        INPUT_FILE_NAME, 
                        INSIGHTS_FILE_NAME, 
                        PARENT_CLUSTER_NAME, 
                        NUMBER_OF_SUBCLUSTERS):
        
        self.db_helper.connect()

        insert_query = """
    INSERT INTO run_log (RUN_ID,
    RUN_NAME,
    NUMBER_OF_CLUSTERS, 
    PARENT_CLUSTER_NAME,
    NUMBER_OF_SUBCLUSTERS, 
    CATEGORY, 
    INPUT_FILE_NAME, 
    INSIGHTS_FILE_NAME,
    CONTAINER_NAME,
    ACCOUNT_NAME)
    VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s,%s)
    """
        
        insert_query = self.query_helper(insert_query)

        data = ( RUN_ID,run_name,  
                NUMBER_OF_CLUSTERS, 
                PARENT_CLUSTER_NAME,
                NUMBER_OF_SUBCLUSTERS, CATEGORY, 
                INPUT_FILE_NAME, INSIGHTS_FILE_NAME,
                self.azure_blob_container,
                self.azure_blob_account)
        
        self.db_helper.execute_query(insert_query, data)
        self.db_helper.close_connection()

    def insert_cluster_data(self,RUN_ID,RUN_NAME, 
                         CATEGORY, 
                         INPUT_FILE_NAME, 
                         INSIGHTS_FILE_NAME,
                         CLUSTER_ID, 
                         CLUSTER_NAME, 
                         PARENT_CLUSTER_ID,
                         PARENT_CLUSTER_NAME):
        # Establish a connection to the database
        self.db_helper.connect()
        print("CONNECTED to the database")

        # Define the insert query
        insert_query = """
        INSERT INTO cluster_data (RUN_ID,
        RUN_NAME, 
        CATEGORY, 
        INPUT_FILE_NAME, 
        INSIGHTS_FILE_NAME,
        CLUSTER_ID, 
        CLUSTER_NAME, 
        PARENT_CLUSTER_ID,
        PARENT_CLUSTER_NAME)
        VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s)
        """

        insert_query = self.query_helper(insert_query)
        
        # Prepare the data tuple
        data = (
        RUN_ID,
        RUN_NAME, 
        CATEGORY, 
        INPUT_FILE_NAME, 
        INSIGHTS_FILE_NAME,
        CLUSTER_ID, 
        CLUSTER_NAME, 
        PARENT_CLUSTER_ID,
        PARENT_CLUSTER_NAME)

        try:
            # Execute the insert query with the provided data
            self.db_helper.execute_query(insert_query, data)
            print("Data inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()
            
    def query_helper(self,query):

        if self.db_type == "DUCKDB" or self.db_type == "SQLITE":
            query = query.replace('%s', '?')
        
        return(query)
    
    def get_records(self,query):
               
        select_query = self.query_helper(query)

        print(select_query)

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,)
        self.db_helper.close_connection()
        
        return records
    
    
    def get_run_for_drilling_into_subcluster(self,
                                             cluster_name):
        # Fetch and display all records to verify insertion
        select_query = 'SELECT RUN_ID FROM cluster_data \
              WHERE PARENT_CLUSTER_ID = %s '
        
        select_query = self.query_helper(select_query)

        print(select_query)
        category_to_search = cluster_name

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,[category_to_search])
        self.db_helper.close_connection()

        if records:
            print(records[0][0])
            return records[0][0]
        else:
            return None
    
    def get_run_names_for_category(self,category_name):
        select_query = 'SELECT RUN_ID,RUN_NAME FROM run_log \
              WHERE CATEGORY = %s '
        
        select_query = self.query_helper(select_query)

        print(select_query)
        category_to_search = category_name

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,[category_to_search])
        self.db_helper.close_connection()

        if records:
            return records
        else:
            return None
        
    def get_parent_cluster_name(self,category_name,
                                run_name):
        
        select_query ="""

            SELECT DISTINCT(CLUSTER_NAME)
            FROM cluster_data
            WHERE CATEGORY = %s \
            AND RUN_NAME = %s 

            """
        
        select_query = self.query_helper(select_query)

        print(select_query)

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,
                    [category_name,run_name])
        return(records)
    
    def get_file_name_from_category(self,category_name):

        select_query ="""

            SELECT INPUT_FILE_NAME
            FROM category_data
            WHERE CATEGORY = %s 

            """
        
        select_query = self.query_helper(select_query)

        print(select_query)

        self.db_helper.connect()
        records = self.db_helper.fetch_all(select_query,
                    [category_name])
        return(records[0][0])
    
    def insert_category_data(self,CATEGORY , 
                    INPUT_FILE_NAME , 
                    DESCRIPTION_COL , 
                    CHALLENGE_COL , 
                    SOLUTION_COL ):
        # Establish a connection to the database
        self.db_helper.connect()
        print("CONNECTED to the database")

        print(f"Category Data : {CATEGORY}")
        print(f"INPUT_FILE_NAME Data : {INPUT_FILE_NAME}")
        print(f"DESCRIPTION_COL Data : {DESCRIPTION_COL}")
        print(f"CHALLENGE_COL Data : {CHALLENGE_COL}")
        print(f"SOLUTION_COL Data : {SOLUTION_COL}")
              

        # Define the insert query
        insert_query = """
        INSERT INTO  category_data (
                    CATEGORY , 
                    INPUT_FILE_NAME , 
                    DESCRIPTION_COL , 
                    CHALLENGE_COL , 
                    SOLUTION_COL 
                    )
        VALUES (%s, %s, %s, %s, %s)
        """

        insert_query = self.query_helper(insert_query)
        print(insert_query)
        
        # Prepare the data tuple
        data = (CATEGORY , 
                    INPUT_FILE_NAME , 
                    DESCRIPTION_COL , 
                    CHALLENGE_COL , 
                    SOLUTION_COL )

        try:
            # Execute the insert query with the provided data
            self.db_helper.execute_query(insert_query, data)
            print("Data inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()
    
    def insert_category_info(
            self,
            file_data,
            file_name:str,
            category: str ,
            description: str ,
            challenge: str ,
            solution: str 
    ):
        
        self.azure_blob_helper.upload_blob(
            file_data,
            file_name
        )

        print(f"{file_name} has been successfully uploaded")

        self.insert_category_data(CATEGORY = category, 
                    INPUT_FILE_NAME = file_name , 
                    DESCRIPTION_COL = description, 
                    CHALLENGE_COL = challenge , 
                    SOLUTION_COL = solution )
        
        print(f"{file_name} has been successfully updated \
              in the Category Log")

        return True
    
    def get_guid(self):
        import uuid
        return(str(uuid.uuid4()))
    
    

