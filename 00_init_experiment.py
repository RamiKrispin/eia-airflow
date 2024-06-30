import mlflow
from datetime import datetime
import pytz
import os

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


def set_mlflow_experiment(path, experiment_name):

    # Set MLflow experiment
    mlflow.set_tracking_uri(mlflow_path)
    ex = mlflow.get_experiment_by_name(experiment_name)
    if ex is None:
        new_experiment = True
        mlflow.create_experiment(name = experiment_name,
                                 artifact_location= path,
                                 tags = tags)
    else:
        new_experiment = False

    meta = mlflow.get_experiment_by_name(experiment_name)

    return meta


def set_run_name():
    tz_utc = pytz.timezone("UTC")
    run_name = datetime.now(tz_utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    return run_name


run_tags = {
     "updates_available": False,
     "data_refresh": False
}


def update_tags(run_name, experiment_id, tags):
    run = mlflow.start_run(run_name = run_name, 
                           experiment_id= experiment_id, 
                           tags = tags)
    
    
    return run

output = {
    "run_name": run_name,
    "experiment_id": meta.experiment_id,
    "run_id": run.info.run_id
    }

#return values to Xcom
print(output)