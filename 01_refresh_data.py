import os
import eia_etl as etl
from datetime import datetime
import pandas as pd
import mlflow


REFRESH = os.getenv('REFRESH')
ref = eval(REFRESH)
# Functions
def get_tags(run_id):
    run_meta = mlflow.get_run(run_id = run_id)
    tags = run_meta.data.tags

    return tags

def get_params(run_id):
    run_meta = mlflow.get_run(run_id = run_id)
    params = run_meta.data.params

    return params

def parse_boolean(input):
    if input.lower() == "true":
        return True
    elif input.lower() == "false":
        return False
    else:
        return None

# Parameters
experiment_name = "data_refresh"
mlflow_path = "file:///scripts/airflow/mlruns"
tags = {"type": "datarefresh", "version": "0.0.0.9000"}
api_routh = "electricity/rto/region-data/"
api_path = api_routh + "data"
eia_api_key = os.getenv("EIA_API_KEY")
data_folder = "scripts/airflow/data"
facets = {
    "respondent": "US48",
    "type": "D"
}
offset = 7 * 24
data_folder = "scripts/airflow/data"


mlflow.set_tracking_uri(mlflow_path)


ref["experiment_id"]

t = get_tags(run_id=ref["run_id"])
p = get_params(run_id=ref["run_id"])
print(t)
print(p)

# print(type(p["start"]))

# status = parse_boolean(t["updates_available"])


# def update_data(start, end, api_key, api_path, facets, offset, verbose = False):
#     new_data = etl.eia_data_refresh(start = start, 
#                                     end = end, 
#                                     api_key = api_key, 
#                                     api_path = api_path, 
#                                     facets = facets, 
#                                     offset = offset,
#                                     verbose = verbose)
#     return new_data 

# if status == True:
#     start = datetime.strptime(p["start"], "%Y-%m-%d %H:%M:%S")
#     end = datetime.strptime(p["end"], "%Y-%m-%d %H:%M:%S")
#     new_data = update_data(start = start, 
#             end = end, 
#             api_key = eia_api_key, 
#             api_path = api_path, 
#             facets = facets, 
#             offset = offset, 
#             verbose = False)
#     if len(new_data.data) > 0:
#         append_data = etl.append_new_data(data_path = data_folder + "/us48.csv",
#                            log_path = data_folder + "/us48_metadata.csv",
#                            new_data = new_data,
#                            save = False,
#                            verbose = False)
#         ref["comment"] = "refreshed the data"
#         data_refresh = True
#     else:
#         ref["comment"] = "data refresh field, please check the logs..."
# elif status == False:
#     ref["comment"] = "No new data is available"
#     data_refresh = False
# else: 
#     ref["comment"] =  "The xcom value is invalid, please check the logs"
#     data_refresh = False


# print(data_refresh)












