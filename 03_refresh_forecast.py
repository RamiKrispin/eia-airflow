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
    

# Pull MLflow experiment
mlflow.set_tracking_uri(mlflow_path)
meta = mlflow.get_experiment_by_name(experiment_name)


t = get_tags(run_id=run_id)
p = get_params(run_id=run_id)

print(t)