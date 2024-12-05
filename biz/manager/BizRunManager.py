import sys
sys.path.append("../")

from itops.runmanager.runmamanger import RunManager
from itops.insights.run_insights import InsightsManager
from itops.llm.azureopenaimanager.azure_open_ai_helper import \
AzureOpenAIManager
from itops.db.mysql.mysqlhelper import MySQLHelper
from itops.db.duckdb.duckdbhelper import DuckDBDatabaseHelper
from itops.db.sqlite.sqlitehelper import SQLiteDatabaseHelper
from config.configs import CONFIGS
import pandas as pd

class BizRunManager:
        def __init__(self,
                 category_name,
                 embedding_model_name,
                 db_type = "SQLITE",
                 ):
          
          self.db_type = db_type
          self.get_db_helper()

          self.llm_helper =AzureOpenAIManager(endpoint=CONFIGS.AZURE_OPENAI_ENDPOINT,
                                    api_key =CONFIGS.AZURE_OPENAI_API_KEY,
                                    deployment_id=CONFIGS.AZURE_OPENAI_DEPLOYMENT_ID,
            api_version = "2024-02-01")

          self.run_manager = RunManager(category_name,
                 embedding_model_name,
                 azure_open_ai_helper= self.llm_helper,
                 azure_blob_account = CONFIGS.AZURE_BLOB_STORAGE_ACCOUNT,
                 azure_blob_container = CONFIGS.AZURE_BLOB_STORAGE_CONTAINER,
                 azure_storage_key = CONFIGS.AZURE_BLOB_STORAGE_KEY,
                 db_helper= self.db_helper,
                 db_type = self.db_type,
                 )
          
          self.insights_manager =InsightsManager(
                azure_blob_account = CONFIGS.AZURE_BLOB_STORAGE_ACCOUNT,
                 azure_blob_container = CONFIGS.AZURE_BLOB_STORAGE_CONTAINER,
                 azure_storage_key = CONFIGS.AZURE_BLOB_STORAGE_KEY,
                 db_helper= self.db_helper,
                 db_type = self.db_type,
                 llm_helper=self.llm_helper)

        def get_db_helper(self):
            if self.db_type == "DUCKDB":
                  self.db_helper = DuckDBDatabaseHelper("itops.duckdb")
            elif self.db_type == "MYSQL":
                  self.db_helper = MySQLHelper(CONFIGS.HOST,
                               CONFIGS.USERNAME_MYSQL,
                               CONFIGS.PASSWORD, "itops")
            elif self.db_type =="SQLITE":
                  self.db_helper = SQLiteDatabaseHelper("itops.db")
          
        def run_cluster(self,
                    run_name,
                    category_name,
                    input_file_name,
                    num_clusters):
        
          prompt_name =  "Please extract the theme \
              of the provided context in Maximum 5 words"
          

          self.run_manager.run_cluster(run_name =run_name,
                    category_name =category_name,
                    input_file_name =input_file_name,
                    num_clusters =num_clusters,
                    prompt=prompt_name)
          
        def rerun_cluster(self,
                    run_name,
                    category_name,
                    num_clusters):
             
                     prompt_name =  "Please extract the theme \
              of the provided context in Maximum 5 words"
          

                     self.run_manager.rerun_cluster(run_name,
                    category_name,
                    prompt_name,
                    num_clusters)
                     
        def rerun_sub_cluster(self,
                    run_name,
                    category_name,
                    num_clusters,
                    parent_cluster_name,
                    parent_run_name):
              
               prompt_name =  "Please extract the theme \
              of the provided context in Maximum 5 words"

               return(self.run_manager.rerun_sub_cluster(
                    run_name,
                    category_name,
                    prompt_name,
                    num_clusters,
                    parent_cluster_name,
                    parent_run_name))
               
        def get_insights_solutions(self,run_name,
                                   category_name,
                                   cluster_name,
                     description_column_name): 
              
              prompt = """
                        Please list the 5 recommended solutions from the context
                       """
              return(self.insights_manager.get_insights_specific_attr(
                    run_name=run_name,
                    cluster_name=cluster_name,
                    category_name = category_name,
                    description_column_name=description_column_name,
                    prompt = prompt
              ))
        
        def get_insights_challenges(self,run_name,
                                    category_name,
                                    cluster_name,
                     description_column_name): 
              
              prompt = """
                        Please list the 5 pain points from the context
                       """
              return(self.insights_manager.get_insights_specific_attr(
                    run_name=run_name,
                    cluster_name=cluster_name,
                    category_name  = category_name,
                    description_column_name=description_column_name,
                    prompt = prompt
              ))
        
        def get_cluster_counts(self,
                               run_name,category_name):
               clusters = self.insights_manager.get_cluster_counts(run_name,
                                                                   category_name,
                                                                   None)
   
               clusters_df = pd.DataFrame(clusters)
               clusters_df = clusters_df.sort_values(by="CLUSTERS",ascending= False)
               return(clusters_df.reset_index().to_dict(orient="records"))

        def get_run_names(self):
              select_query = """
              SELECT RUN_ID,RUN_NAME
              FROM RUN_LOG 
              """

              records = self.run_manager.get_records(select_query)
            
              return(records)
              
        def get_run_for_drilling_into_subcluster(self,
                                                cluster_name):
            
            return(self.run_manager.get_run_for_drilling_into_subcluster(cluster_name))
        
        def get_category_names(self):
              select_query = """
              SELECT DISTINCT(CATEGORY)
              FROM CATEGORY_DATA 
              """

              records = self.run_manager.get_records(select_query)
            
              records_list = []
              for record in records:
                    records_list.append(record[0])
              return(records_list)
        
        
        def get_run_names_for_category(self,category_name):
              
              records=self.run_manager.get_run_names_for_category(category_name)
              
              if records is None:
                    return None
              
              return(records)
        
        def get_parent_cluster_name(self,category_name,
                                run_name):
              
              records=self.run_manager.get_parent_cluster_name(
                    category_name,
                    run_name)
              
              if records is None:
                    return None
              records_list = []
              for record in records:
                    records_list.append(record[0])
              
              return(records_list)
        
        def run_cluster_from_category(self,
                    run_name,
                    category_name,
                    num_clusters):
              
              file_name = self.run_manager.get_file_name_from_category(category_name)

              self.run_cluster(run_name,
                               category_name,
                               file_name,
                               num_clusters)
        
        def insert_category_info(
            self,
            file_data,
            file_name:str,
            category: str ,
            description: str ,
            challenge: str ,
            solution: str 
    ):
              return(
                    self.run_manager.insert_category_info(
                        file_data,
                        file_name,
                        category ,
                        description ,
                        challenge ,
                        solution
                        )
              )

               
     
          