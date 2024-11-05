import sys
sys.path.append("../../")

from itops.db.mysql.mysqlhelper import MySQLHelper
from itops.config.configs import CONFIGS
mysql_helper = MySQLHelper(CONFIGS.HOST,
                           CONFIGS.USERNAME_MYSQL,
                           CONFIGS.PASSWORD, "itops")

# Connect to the MySQL database
mysql_helper.connect()

# Sample data to insert
sample_data = [
    (1,"Run1", "ClusterA", 5, "ParentCluster1", 2, "Category1", "input_file_1.txt", "insights_file_1.txt"),
    (2,"Run2", "ClusterB", 3, "ParentCluster2", 1, "Category2", "input_file_2.txt", "insights_file_2.txt"),
    (3,"Run3", "ClusterC", 4, "ParentCluster3", 3, "Category3", "input_file_3.txt", "insights_file_3.txt"),
]

# Insert sample data into run_log table
insert_query = """
    INSERT INTO run_log (ID,RUN_NAME, CLUSTER_NAME, NUMBER_OF_CLUSTERS, PARENT_CLUSTER_NAME,
                            NUMBER_OF_SUBCLUSTERS, CATEGORY, INPUT_FILE_NAME, INSIGHTS_FILE_NAME)
    VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s)
"""

for data in sample_data:
    mysql_helper.execute_query(insert_query, data)

print("Sample data inserted successfully.")

# Fetch and display all records to verify insertion
select_query = "SELECT * FROM run_log"
records = mysql_helper.fetch_all(select_query)

for record in records:
    print(record)

# Close the connection
mysql_helper.close_connection()
