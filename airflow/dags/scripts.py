import mlflow
from datetime import datetime
import pytz
import os


def get_env_vars():
    class env_vars:
        def __init__(self, experiment_name, mlflow_path, tags, api_routh, api_path, eia_api_key, data_folder,facets, offset):
            self.experiment_name = experiment_name
            self.mlflow_path = mlflow_path
            self.tags = tags
            self.api_routh = api_routh
            self.api_path = api_path
            self.eia_api_key = eia_api_key
            self.data_folder = data_folder
            self.facets = facets
            self.offset = offset


    experiment_name = os.getenv("experiment_name")
    mlflow_path = os.getenv("mlflow_path")
    tags = os.getenv("tags")
    api_routh = os.getenv("api_routh")
    api_path = os.getenv("api_path")
    eia_api_key = os.getenv("eia_api_key")
    data_folder = os.getenv("data_folder")
    facets = os.getenv("facets")
    offset = os.getenv("offset")

    output = env_vars(experiment_name  = experiment_name,
                      mlflow_path = mlflow_path,
                      tags = tags,
                      api_routh = api_routh,
                      api_path = api_path,
                      eia_api_key = eia_api_key,
                      data_folder = data_folder,
                      facets = facets,
                      offset = offset)
    return output

    

def set_mlflow_experiment(path, name, tags, tz = "UTC"):
    run_tags = {
     "updates_available": False,
     "data_refresh": False
    }
    mlflow.set_tracking_uri(path)
    ex = mlflow.get_experiment_by_name(name)
    if ex is None:
        new_experiment = True
        mlflow.create_experiment(name = experiment_name,
                             artifact_location= mlflow_path,
                             tags = tags)
    else:
        new_experiment = False
    
    meta = mlflow.get_experiment_by_name(name)
    run_tz = pytz.timezone(tz)
    run_name = datetime.now(run_tz).astimezone().strftime("%Y-%m-%d %H:%M %Z")

    run = mlflow.start_run(run_name = run_name, 
                       experiment_id= meta.experiment_id, 
                       tags = run_tags)
    
    
    output = {
        "run_name": run_name,
        "experiment_id": meta.experiment_id,
        "run_id": run.info.run_id,
        "new_experiment": new_experiment
    }
    return output


def get_xcom_value(task_id):
    xcom_value = ti.xcom_pull(task_ids = task_id)
    return xcom_value

