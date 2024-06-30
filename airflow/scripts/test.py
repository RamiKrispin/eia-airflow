import os
import mlflow
import json
import eia_etl as etl
import eia_api
import datetime

facets = {
    "respondent": "US48",
    "type": "D"
}

tags = {"type": "datarefresh", "version": "0.0.0.9000"}

experiment_name = "data_refresh"
mlflow_path = "file:///../mlruns"
experiment_name= "data_refresh"
mlflow_path = "file:///mlruns/"
tags = eval(json.dumps(tags))
api_routh = "electricity/rto/region-data/"
api_path = "electricity/rto/region-data/data"
eia_api_key = os.getenv("EIA_API_KEY")
data_folder = "./data"
facets = eval(json.dumps(facets))
offset = int("168")
api_key = os.getenv("EIA_API_KEY")
experiment_id = "140762455412249357"
run_id = "4ba80b4301c3429db3a107d32d84c341"

mlflow_path = "file:///mlruns/"
mlflow.set_tracking_uri(mlflow_path)

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

mlflow.set_tracking_uri(mlflow_path)
meta = mlflow.get_experiment_by_name(experiment_name)


t = get_tags(run_id=run_id)
p = get_params(run_id=run_id)

status = parse_boolean(t["updates_available"])

start = p["start"]


start = datetime.datetime.strptime(p["start"] , "%Y-%m-%d %H:%M")
end = datetime.datetime.strptime(p["end"] , "%Y-%m-%d %H:%M")
print(start)
print(end)
new_data = etl.eia_data_refresh(start = start, 
                                    end = end, 
                                    api_key = api_key, 
                                    api_path = api_path, 
                                    facets = facets, 
                                    offset = offset,
                                    verbose = True)
