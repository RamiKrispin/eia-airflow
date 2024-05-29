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



def put_values_using_xcom(**kwargs):
    test_msg = 'the_message'
    print("message to push: '%s'" % test_msg)
    ti = kwargs["ti"]
    ti.xcom_push(key="Test_Message", value=test_msg)


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
        command = "/opt/forecasting-poc/bin/python3.10 /scripts/00_check_status.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        api_version="auto",
        xcom_all= False,
        cpus = 1,
        mount_tmp_dir= False,
        environment={"EIA_API_KEY": os.getenv("EIA_API_KEY")},
        mounts= [
            Mount(source = "/Users/ramikrispin/Personal/poc/eia-airflow/", target = "/scripts", type = "bind")
        ]
    )


    taskB = DockerOperator(
        task_id = "task_B",
        image = "docker.io/rkrispin/forecast-poc:0.0.0.9011",
        command = "/opt/forecasting-poc/bin/python3.10 /scripts/01_refresh_data.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        api_version="auto",
        xcom_all= False,
        cpus = 1,
        mount_tmp_dir= False,
        environment={"EIA_API_KEY": os.getenv("EIA_API_KEY"),
                     'REFRESH': "{{ ti.xcom_pull(task_ids='task_A') }}"},
        mounts= [
            Mount(source = "/Users/ramikrispin/Personal/poc/eia-airflow/", target = "/scripts", type = "bind")
        ]
    )

    taskC = DockerOperator(
        task_id = "task_C",
        image = "docker.io/rkrispin/forecast-poc:0.0.0.9011",
        command = "/opt/forecasting-poc/bin/python3.10 /scripts/02_refresh_forecast.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        api_version="auto",
        xcom_all= False,
        cpus = 1,
        mount_tmp_dir= False,
        environment={"EIA_API_KEY": os.getenv("EIA_API_KEY"),
                     'REFRESH': "{{ ti.xcom_pull(task_ids='task_A') }}"},
        mounts= [
            Mount(source = "/Users/ramikrispin/Personal/poc/eia-airflow/", target = "/scripts", type = "bind")
        ]
    )


    taskD = PythonOperator(
        task_id = "task_D",
        
        provide_context=True,
        python_callable=put_values_using_xcom
    )

taskA >> taskB >> taskC
taskA >> taskD