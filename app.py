# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from biz.manager.BizRunManager import BizRunManager

app = FastAPI()

description_column_name = "Text"
MODEL_NAME = "all-MiniLM-L6-v2"

# Initialize your BizRunManager
biz_run_manager = BizRunManager(
    description_column_name=description_column_name,
    embedding_model_name=MODEL_NAME,
    db_type="SQLITE"  # or "MYSQL", "DUCKDB"
)

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

@app.post("/run-cluster")
async def run_cluster(request: RunClusterRequest):
    try:
        biz_run_manager.run_cluster(
            run_name=request.run_name,
            category_name=request.category_name,
            input_file_name=request.input_file_name,
            num_clusters=request.num_clusters,
        )
        return {"message": "Cluster run initiated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rerun-cluster")
async def rerun_cluster(request: RerunClusterRequest):
    try:
        biz_run_manager.rerun_cluster(
            run_name=request.run_name,
            category_name=request.category_name,
            num_clusters=request.num_clusters,
        )
        return {"message": "Cluster rerun initiated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rerun-sub-cluster")
async def rerun_sub_cluster(request: RerunSubClusterRequest):
    try:
        biz_run_manager.rerun_sub_cluster(
            run_name=request.run_name,
            category_name=request.category_name,
            num_clusters=request.num_clusters,
            parent_cluster_name=request.parent_cluster_name,
            parent_run_name=request.parent_run_name,
        )
        return {"message": "Sub-cluster rerun initiated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-insights-solutions")
async def get_insights_solutions(request: InsightsRequest):
    try:
        solutions = biz_run_manager.get_insights_solutions(
            run_name=request.run_name,
            cluster_name=request.cluster_name,
            description_column_name=request.description_column_name,
        )
        return {"solutions": solutions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-insights-challenges")
async def get_insights_challenges(request: InsightsRequest):
    try:
        challenges = biz_run_manager.get_insights_challenges(
            run_name=request.run_name,
            cluster_name=request.cluster.name,
            description_column=request.description_column,
        )
        return {"challenges": challenges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/cluster-counts/")
async def read_cluster_counts(request: RunNameRequest):
    return biz_run_manager.get_cluster_counts(request.run_name)

# Run the FastAPI application with Uvicorn server (if running this file directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)