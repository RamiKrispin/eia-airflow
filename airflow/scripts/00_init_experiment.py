import mlflow
from datetime import datetime
import pytz
import os

def get_xcom_value(task_id):
    xcom_value = ti.xcom_pull(task_ids = task_id)
    return xcom_value
  
# Parameters
experiment_name = os.getenv("experiment_name")
mlflow_path = os.getenv("mlflow_path")
tags = eval(os.getenv("tags"))
api_routh = os.getenv("api_routh")
api_path = os.getenv("api_path")
eia_api_key = os.getenv("eia_api_key")
data_folder = os.getenv("data_folder")
facets = eval(os.getenv("facets"))
offset = int(os.getenv("offset"))


# Set MLflow experiment
mlflow.set_tracking_uri(mlflow_path)
ex = mlflow.get_experiment_by_name(experiment_name)
if ex is None:
    print(experiment_name)
    new_experiment = True
    mlflow.create_experiment(name = experiment_name,
                             artifact_location= mlflow_path,
                             tags = tags
                            )
else:
    new_experiment = False


meta = mlflow.get_experiment_by_name(experiment_name)

tz_utc = pytz.timezone("UTC")
run_name = datetime.now(tz_utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")


run_tags = {
     "updates_available": False,
     "data_refresh": False
}

run = mlflow.start_run(run_name = run_name, 
                       experiment_id= meta.experiment_id, 
                       tags = run_tags)

output = {
    "run_name": run_name,
    "experiment_id": meta.experiment_id,
    "run_id": run.info.run_id
    }

# #return values to Xcom
print(output)