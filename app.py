# app/main.py

from fastapi import FastAPI, HTTPException

from biz.manager.BizRunManager import BizRunManager
from api.request_response_model import *

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

description_column_name = "Text"
MODEL_NAME = "all-MiniLM-L6-v2"

# Initialize your BizRunManager
biz_run_manager = BizRunManager(
    description_column_name=description_column_name,
    embedding_model_name=MODEL_NAME,
    db_type="SQLITE"  # or "MYSQL", "DUCKDB"
)


@app.post("/run-cluster")
async def run_cluster(request: RunClusterRequest):
    try:
        biz_run_manager.run_cluster(
            run_name=request.run_name,
            category_name=request.category_name,
            input_file_name=request.input_file_name,
            num_clusters=request.num_clusters,
        )
        return {"message": "Cluster run completed successfully."}
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
        return {"message": "Cluster rerun completed successfully."}
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
        return {"message": "Sub-cluster rerun completed successfully."}
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
            cluster_name=request.cluster_name,
            description_column_name=request.description_column_name,
        )
        return {"challenges": challenges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/cluster-counts/")
async def read_cluster_counts(request: RunNameRequest):
    return biz_run_manager.get_cluster_counts(request.run_name)

@app.post("/get-run-names/")
async def read_run_names():
    return biz_run_manager.get_run_names()

@app.post("/get-category-names/")
async def read_category_names():
    return biz_run_manager.get_category_names()

@app.post("/get-run-name-for-drill-down/")
async def read_run_names(request: ClusterNameRequest):
    response = biz_run_manager.get_run_for_drilling_into_subcluster(request.cluster_name)

    return({"run_name": response})

@app.post("/get-run-names-for-category/")
async def read_run_names_for_category(request :CategoryNameRequest):
    return(biz_run_manager.get_run_names_for_category(request.category_name))
    
@app.post("/get-parent-cluster-names/")
async def read_parent_cluster_names(request :CategoryAndRunNameRequest):
    return(biz_run_manager.get_parent_cluster_name
           (request.category_name,request.run_name))

@app.post("/run-clusters-from-category/")
async def run_clusters_from_category(request :RerunClusterRequest):
    return(biz_run_manager.run_cluster_from_category(request.run_name,
                                                     request.category_name,
                                                     request.num_clusters))
           
    
# Run the FastAPI application with Uvicorn server (if running this file directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)