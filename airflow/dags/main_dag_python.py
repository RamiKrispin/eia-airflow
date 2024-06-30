# airflow webserver --port 8080
# airflow scheduler
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from docker.types import Mount

import os
import json

default_args = {
    "owner" : "Rami"
}

# Parameters


facets = {
    "respondent": "US48",
    "type": "D"
}

tags = {"type": "datarefresh", "version": "0.0.0.9000"}
env = {
"experiment_name": "data_refresh",
"mlflow_path": "file:///mlruns/",
"tags": json.dumps(tags),
"api_routh": "electricity/rto/region-data/",
"api_path": "electricity/rto/region-data/data",
"eia_api_key": os.getenv("EIA_API_KEY"),
"data_folder": "/data",
"facets": json.dumps(facets),
"offset": "168"
}
env2 = env
env2["xcom"] = "{{ ti.xcom_pull(task_ids='task_A') }}"

xcom =  "{{ ti.xcom_pull(task_ids='task_A') }}"

EIA_API_KEY = os.getenv('EIA_API_KEY')

def get_xcom_value(task_id):
    xcom_value = ti.xcom_pull(task_ids = task_id)
    return xcom_value

with DAG(
    dag_id = "eia_refresh_python",
    description = "EIA data and forecast pipeline",
    default_args =  default_args,
    start_date= days_ago(1),
    schedule_interval = "@daily",
    tags = ["test", "bash", "python"],
    template_searchpath = "/airflow/scripts/"
) as dag:
    taskA = BashOperator(
        task_id = "task_A",
        bash_command = "/opt/forecasting-poc/bin/python3 /airflow/scripts/00_init_experiment.py",
        env = env
    )
    taskB = BashOperator(
        task_id = "task_B",
        bash_command = "/opt/forecasting-poc/bin/python3 /airflow/scripts/01_check_status.py",
        env = env2
    )
    taskC = BashOperator(
        task_id = "task_C",
        bash_command = "/opt/forecasting-poc/bin/python3 /airflow/scripts/02_refresh_data.py",
        env = env2
    )
    
taskA >> taskB >> taskC