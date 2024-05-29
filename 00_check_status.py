import pandas as pd
import eia_api
import eia_etl as etl
import os
import mlflow
import pytz
from datetime import datetime


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

# Set MLflow
mlflow.set_tracking_uri(mlflow_path)
ex = mlflow.get_experiment_by_name(experiment_name)
if ex is None:
    new_experiment = True
    mlflow.create_experiment(name = experiment_name,
                             artifact_location= mlflow_path,
                             tags = tags)
else:
    new_experiment = False

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
status["new_experiment"] = new_experiment


tz_utc = pytz.timezone("UTC")
run_name = datetime.now(tz_utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
status["run_name"] = run_name
status["experiment_id"] = meta.experiment_id
params = {
    "start": status["start"],
    "end": status["end"],
}
run_tags = {
     "updates_available": status["status"],
     "data_refresh": False
}


with mlflow.start_run(run_name = run_name,
    experiment_id= meta.experiment_id, tags = run_tags) as run:
    mlflow.log_params(params = params)

status["artifact_uri"]  = run.info.artifact_uri
status["run_id"]  = run.info.run_id

print(status)