from pydantic import BaseModel

# Define request models for input validation
class RunClusterRequest(BaseModel):
    run_name: str
    category_name: str
    input_file_name: str
    num_clusters: int

class RerunClusterRequest(BaseModel):
    run_name: str
    category_name: str
    num_clusters: int

class RerunSubClusterRequest(BaseModel):
    run_name: str
    parent_run_name: str
    parent_cluster_name: str
    category_name: str
    num_clusters: int

class InsightsRequest(BaseModel):
    run_name: str
    cluster_name: str
    description_column_name: str

# Define a Pydantic model for incoming requests
class RunNameRequest(BaseModel):
    run_name: str

class ClusterNameRequest(BaseModel):
    cluster_name:str

class CategoryNameRequest(BaseModel):
    category_name:str