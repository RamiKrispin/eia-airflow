import pandas as pd
import eia_api
import eia_etl as etl
import os
import mlflow
import pytz
from datetime import datetime


# Parameters
experiment_name = os.getenv("experiment_name")
mlflow_path = os.getenv("mlflow_path")
tags = os.getenv("tags")
api_routh = os.getenv("api_routh")
api_path = os.getenv("api_path")
eia_api_key = os.getenv("eia_api_key")
data_folder = os.getenv("data_folder")
facets = os.getenv("facets")
offset = os.getenv("offset")

xcom = os.getenv('xcom')
ref = eval(xcom)
run_name = ref["run_name"]
experiment_id = ref["experiment_id"]
run_id = ref["run_id"]
print(run_id)
print(xcom)
# Functions
def get_tags(run_id):
    run_meta = mlflow.get_run(run_id = run_id)
    tags = run_meta.data.tags

    return tags


# Pull MLflow experiment
mlflow.set_tracking_uri(mlflow_path)
meta = mlflow.get_experiment_by_name(experiment_name)

def check_updates(metadata_path, api_key, offset = 8, api_routh = api_routh):
    
    log_file = etl.load_log(path = metadata_path)
    start = log_file.start

    metadata = etl.get_api_end(api_key = api_key, 
                               api_path =  api_routh, 
                               offset = offset)
    end_fix = metadata.end_fix

    if(end_fix > start):
        status = True
    else:
        status = False
    
    output = {"start": start.strftime("%Y-%m-%d %H:%M"),
              "end": end_fix.strftime("%Y-%m-%d %H:%M"),
              "status": status}
    
    return output
    





status = check_updates(metadata_path = data_folder + "/us48_metadata.csv", api_key = eia_api_key, offset = 8)

params = {
    "start": status["start"],
    "end": status["end"],
}
run_tags = {
     "updates_available": status["status"],
     "data_refresh": False
}


with mlflow.start_run(run_id = run_id,
    experiment_id= experiment_id, tags = run_tags) as run:
    mlflow.log_params(params = params)


t = get_tags(run_id = run_id)
