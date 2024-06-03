from datetime import datetime, timedelta
from airflow.utils.dates import days_ago

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from docker.types import Mount

import os

default_args = {
    "owner" : "Rami"
}

# Parameters
env = {
"experiment_name": "data_refresh",
"mlflow_path": "file:///scripts/airflow/mlruns",
"tags": {"type": "datarefresh", "version": "0.0.0.9000"},
"api_routh": "electricity/rto/region-data/",
"api_path": "electricity/rto/region-data/data",
"eia_api_key": os.getenv("EIA_API_KEY"),
"data_folder": "scripts/airflow/data",
"facets": {
    "respondent": "US48",
    "type": "D"
},
"offset": 7 * 24
}

env2 = env
env2["xcom"] = "{{ ti.xcom_pull(task_ids='task_A') }}"

EIA_API_KEY = os.getenv('EIA_API_KEY')

def get_xcom_value(task_id):
    xcom_value = ti.xcom_pull(task_ids = task_id)
    return xcom_value

with DAG(
    dag_id = "eia_refresh",
    description = "EIA data and forecast pipeline",
    default_args =  default_args,
    start_date= days_ago(1),
    schedule_interval = "@daily",
    tags = ["test", "bash", "python"],
    template_searchpath = "/airflow/scripts/"
) as dag:
    taskA = DockerOperator(
        task_id = "task_A",
        image = "docker.io/rkrispin/forecast-poc:0.0.0.9011",
        command = "/opt/forecasting-poc/bin/python3.10 /scripts/00_init_experiment.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        api_version="auto",
        xcom_all= False,
        cpus = 1,
        mount_tmp_dir= False,
        environment= env,
        mounts= [
            Mount(source = "/Users/ramikrispin/Personal/poc/eia-airflow/", target = "/scripts", type = "bind")
        ]
    )

    taskB = DockerOperator(
        task_id = "task_B",
        image = "docker.io/rkrispin/forecast-poc:0.0.0.9011",
        command = "/opt/forecasting-poc/bin/python3.10 /scripts/01_check_status.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        api_version="auto",
        xcom_all= False,
        cpus = 1,
        mount_tmp_dir= False,
        environment= env2,
        mounts= [
            Mount(source = "/Users/ramikrispin/Personal/poc/eia-airflow/", target = "/scripts", type = "bind")
        ]
    )


    taskC = DockerOperator(
        task_id = "task_C",
        image = "docker.io/rkrispin/forecast-poc:0.0.0.9011",
        command = "/opt/forecasting-poc/bin/python3.10 /scripts/02_refresh_data.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        api_version="auto",
        xcom_all= False,
        cpus = 1,
        mount_tmp_dir= False,
        environment= env2,
        mounts= [
            Mount(source = "/Users/ramikrispin/Personal/poc/eia-airflow/", target = "/scripts", type = "bind")
        ]
    )

    taskD = DockerOperator(
        task_id = "task_D",
        image = "docker.io/rkrispin/forecast-poc:0.0.0.9011",
        command = "/opt/forecasting-poc/bin/python3.10 /scripts/03_refresh_forecast.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        api_version="auto",
        xcom_all= False,
        cpus = 1,
        mount_tmp_dir= False,
        environment= env2,
        mounts= [
            Mount(source = "/Users/ramikrispin/Personal/poc/eia-airflow/", target = "/scripts", type = "bind")
        ]
    )


taskA >> taskB >> taskC >> taskD
