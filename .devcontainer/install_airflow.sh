#!/usr/bin/env bash

VENV_NAME=$1
USERNAME=$2
FIRST=$3
LAST=$4 
ROLE=$5 
PASSWORD=$6 
EMAIL=$7


source /opt/$VENV_NAME/bin/activat

PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" 
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
     && rm -rf /var/lib/apt/lists/*

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
pip install apache-airflow-providers-docker


airflow db migrate 
airflow users create \
    --username $USERNAME \
    --firstname $FIRST \
    --lastname $LAST \
    --role $ROLE \
    --password $PASSWORD \
    --email $EMAIL

# airflow webserver --port 8080
# airflow scheduler