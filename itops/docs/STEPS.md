# BASICS   

1.  Read the File
2.  Get the RELEVANT COLUMNS         
3.  Use LLM to extract the Themes for the Description COLUMN. This is a COSTLY thing. In cases of RERUN / RERUN with Sub Clusters ,Reuse the Data                    
4. Use Embeddings to calculate the Embeddings of the Description COLUMN           
5. Do Clustering based on the Number of Clusters

# MAIN PARAMETERS   
What are the different parameters which controls the process

1. Category
2. Number of Clusters
3. Description COLUMN
4. OPEN and CLOSE TIME of Ticket

# RUN STORE    
For each Run store the following
* Run Name
* Category Name
* Input File
* Insights File
* Number of Clusters
* For the Sub Cluster, to maintain the PARENT CHILD relationship store the following             
  - Parent Cluster Name
  - Number of Sub Clusters

# CLUSTER RELATIONSHIPS  Information STORE 
The Cluster Information Store stores the Cluster Name and its Parent.   

# CLUSTER STATS  STORE 
The Cluster STATS Store stores the STATS of the Cluster. 

# SCENARIOS 
We have 3 major scenarios

1. RUN CLUSTER
2. RERUN CLUSTER
3. RERUN SUB CLUSTER

## SCENARIO - RUN CLUSTER       

1. Generate Themes
2. Generate Embeddings
3. Generate Clusters
4. Store the Insights in BLOB
5. Update the RUN LOG with the following parameters
    * Run Name
    * Category Name
    * Input File
    * Insights File
    * Number of Clusters
6.
Update the Cluster Information Store with the following       
For every Run , there will be N Clusters          

* Run Name
* Category Name
* Input File
* Insights File
* Number of Clusters
* Cluster Name 
* Parent Cluster Name is NONE Here

## SCENARIO - RERUN CLUSTER       


1. DO NOT Generate Themes

    Query the RUN LOG 

    Input Parameters :  Category Name 
    and the Parent Cluster is NOT Present

    Get the Insights File

    Read the Insights File and Get the Themes and the Other Columns


2. Generate Embeddings
3. Generate Clusters
4. Store the Insights in BLOB
5. Update the RUN LOG with the following parameters
    * Run Name
    * Category Name
    * Input File
    * Insights File
    * Number of Clusters
6.

The Cluster Information Store stores the Cluster Name and its Parent.

Update the Cluster Information Store with the 

For every Run , there will be N Clusters 

* Run Name
* Category Name
* Input File
* Insights File
* Number of Clusters
* Cluster Name 
* Parent Cluster Name is NONE Here

## SCENARIO - RERUN SUB CLUSTER    

1. DO NOT Generate Themes

    Query the RUN LOG 

    Input Parameters :  Category Name 
    and the Parent Cluster = Parent Cluster Name
    [ The RUN Number if provided is better ]

    Get the Insights File

    Read the Insights File and Get the Themes and the Other Columns


2. Generate Embeddings
3. Generate Clusters
4. Store the Insights in BLOB
5. Update the RUN LOG with the following parameters
    * Run Name
    * Category Name
    * Input File
    * Insights File
    * Number of Clusters

6.
Update the Cluster Information Store with the following  

For every Run , there will be N Clusters        

* Run Name
* Category Name
* Input File
* Insights File
* Number of Clusters
* Cluster Name 
* Parent Cluster Name HAS A VALUE    


# IMPLEMENTATION DETAILS      

## Files           

1. Input File           
2. Insights File      
   
* Do not download the File [ Use Memory Streams]
* Store the File in Azure BLOB
* All BIG Output should be in Azure BLOB

## Stores 

Store in Relational Database Stores . Done in Maria DB now 

## LLM 

* Azure Open AI Models

## Clustering  

* KMeans   

## Embedding 

* Sentence Transformer Models 
* Azure Open AI ADA

