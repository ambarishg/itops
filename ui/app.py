import streamlit as st
import pandas as pd

import sys
sys.path.append("../")

st.title("Ticket Analysis")

from biz.manager.BizRunManager import BizRunManager

description_column_name = "Text"
MODEL_NAME = "all-MiniLM-L6-v2"
CATEGORY01 = "ITSM"
file_name01 = "ITSM_Data.csv"
run_name01 = "RUN008-15NOV2024"
NUM_CLUSTERS01 =8

# Input fields for user inputs
run_name = st.text_input("Run Name:", value="RUN008-15NOV2024")
CATEGORY = st.text_input("Category Name:", value="ITSM")
NUM_CLUSTERS = st.text_input("Number of Clusters:", value=8)
file_name = st.text_input("File Name:", value=file_name01)
NUM_CLUSTERS = int(NUM_CLUSTERS)

bizrunmanager = BizRunManager(description_column_name,
                              embedding_model_name =MODEL_NAME,
                              db_type="DUCKDB")

if st.button("Run Clusters"):

    bizrunmanager.run_cluster(run_name=run_name,
                          category_name=CATEGORY,
                          input_file_name=file_name,
                          num_clusters=NUM_CLUSTERS)

    df= bizrunmanager.insights_manager.get_input_filename(run_name)


    if df:
        cluster_counts = pd.DataFrame(df["CLUSTER_NAMES"].value_counts())

        st.dataframe(cluster_counts, width=None, height=None)
