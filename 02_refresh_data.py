import os
import eia_etl as etl
from datetime import datetime
import pandas as pd
import mlflow

# Parameters
experiment_name = os.getenv("experiment_name")
mlflow_path = os.getenv("mlflow_path")
tags = os.getenv("tags")
api_routh = os.getenv("api_routh")
api_path = os.getenv("api_path")
eia_api_key = os.getenv("eia_api_key")
data_folder = os.getenv("data_folder")
facets = eval(os.getenv("facets"))

xcom = os.getenv('xcom')
ref = eval(xcom)
run_name = ref["run_name"]
experiment_id = ref["experiment_id"]
run_id = ref["run_id"]
offset = int(os.getenv("offset"))

# Pull MLflow experiment
mlflow.set_tracking_uri(mlflow_path)
meta = mlflow.get_experiment_by_name(experiment_name)


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

def update_data(start, end, api_key, api_path, facets, offset, verbose = False):
    new_data = etl.eia_data_refresh(start = start, 
                                    end = end, 
                                    api_key = api_key, 
                                    api_path = api_path, 
                                    facets = facets, 
                                    offset = offset,
                                    verbose = verbose)
    return new_data 


# Pull MLflow experiment
mlflow.set_tracking_uri(mlflow_path)
meta = mlflow.get_experiment_by_name(experiment_name)


t = get_tags(run_id=run_id)
p = get_params(run_id=run_id)

status = parse_boolean(t["updates_available"])

start = p["start"]

if status == True:
    start = datetime.strptime(p["start"] , "%Y-%m-%d %H:%M")
    end = datetime.strptime(p["end"] , "%Y-%m-%d %H:%M")
    new_data = update_data(start = start, 
            end = end, 
            api_key = eia_api_key, 
            api_path = api_path, 
            facets = facets, 
            offset = offset, 
            verbose = False)
    if len(new_data.data) > 0:
        append_data = etl.append_new_data(data_path = data_folder + "/us48.csv",
                           log_path = data_folder + "/us48_metadata.csv",
                           new_data = new_data,
                           save = False,
                           verbose = False)
        
        last_timestamp = datetime.strftime(new_data.data.period.max(), "%Y-%m-%d %H:%M:%S") 
        
        comment = "refreshed the data"
        data_refresh = True
    else:
        comment = "data refresh field, please check the logs..."
        last_timestamp = None
elif status == False:
    comment = "No new data is available"
    data_refresh = False
    last_timestamp = None
else: 
    comment =  "The xcom value is invalid, please check the logs"
    data_refresh = False
    last_timestamp = None


mlflow.end_run()
tags = {
     "data_refresh": data_refresh,
     "last_point": last_timestamp,
     "comments": comment 
}
run = mlflow.start_run(run_id = run_id, tags = tags)

t = get_tags(run_id=run_id)

print(ref)