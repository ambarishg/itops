from itops.runmanager.runmamanger import RunManager
from itops.insights.run_insights import InsightsManager
from itops.llm.azureopenaimanager.azure_open_ai_helper import \
AzureOpenAIManager
from itops.db.mysql.mysqlhelper import MySQLHelper
from itops.db.duckdb.duckdbhelper import DuckDBDatabaseHelper
from itops.db.sqlite.sqlitehelper import SQLiteDatabaseHelper
from biz.config.configs import CONFIGS

class BizRunManager:
        def __init__(self,
                 description_column_name,
                 embedding_model_name,
                 db_type = "SQLITE",
                 ):
          
          self.db_type = db_type
          self.get_db_helper()

          self.llm_helper =AzureOpenAIManager(endpoint=CONFIGS.AZURE_OPENAI_ENDPOINT,
                                    api_key =CONFIGS.AZURE_OPENAI_API_KEY,
                                    deployment_id=CONFIGS.AZURE_OPENAI_DEPLOYMENT_ID,
            api_version = "2024-02-01")

          self.run_manager = RunManager(description_column_name,
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

               self.run_manager.rerun_sub_cluster(
                    run_name,
                    category_name,
                    prompt_name,
                    num_clusters,
                    parent_cluster_name,
                    parent_run_name)
               
        def get_insights_solutions(self,run_name,cluster_name,
                     description_column_name): 
              
              prompt = """
                        Please list the 5 recommended solutions from the context
                       """
              return(self.insights_manager.get_insights_specific_attr(
                    run_name=run_name,
                    cluster_name=cluster_name,
                    description_column_name=description_column_name,
                    prompt = prompt
              ))
        
        def get_insights_challenges(self,run_name,cluster_name,
                     description_column_name): 
              
              prompt = """
                        Please list the 5 pain points from the context
                       """
              return(self.insights_manager.get_insights_specific_attr(
                    run_name=run_name,
                    cluster_name=cluster_name,
                    description_column_name=description_column_name,
                    prompt = prompt
              ))
               
     
          