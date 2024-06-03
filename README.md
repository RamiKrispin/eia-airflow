# EIA Data Pipeline with AirFlow

This repository provides an example for setting up a data pipeline to refresh data from the EIA API using AirFlow.


## AirFlow Settings

To launch AirFlow using this repo settings with the Dev Containers extenstion you will need to set the below configuration using the `devcontainer.json` file.

### Build Arguments

The AirFlow container is based on the EIA Forecast POC [image](https://github.com/RamiKrispin/eia-poc/blob/main/.devcontainer/Dockerfile.multiple) using the `Dockerfile.airflow` file to add AirFlow using the `build` option. The build configuration is leveraging arguments to customize the AirFlow user settings such as the default folder, AirFlow version, and user info:

``` json
    "build": {
        "dockerfile": "Dockerfile.airflow",
        "context": ".",
        "args": {
            "AIRFLOW_HOME": "/airflow",
            "AIRFLOW_VERSION": "2.9.1",
            "VENV_NAME": "forecasting-poc",
            "AIRFLOW__CORE__LOAD_EXAMPLES": "False",
            "USERNAME": "admin",
            "FIRST": "Rami",
            "LAST": "Krispin",
            "ROLE": "Admin",
            "PASSWORD": "${localEnv:AIRFLOW_PASSWORD:pass}",
            "EMAIL": "my_email@domain.com"
        }
    }
```

### Mounting the AirFlow Folders and Docker Engine

The devcontainer mounts following three folders using the below settings:
- The dags folder
- The scripts folders
- The Docker socket

The first two folders are under the `airflow` folder, and they are used to store the dags and any scripts used during the AirFlow run time. The last mount is of the Docker engine, which is required to run the `DockerOperator`. You should modify the local repo paths:

```shell
 "mounts": [
        "source=/Users/ramikrispin/Personal/poc/eia-airflow/airflow/dags,target=/airflow/dags,type=bind,consistency=cache",
        "source=/Users/ramikrispin/Personal/poc/eia-airflow/airflow/scripts,target=/airflow/scripts,type=bind,consistency=cache",
        "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
    ]
```
**TODO:** Check if the paths can be replaced with environment variables

### API Key

The EIA API key is required to query data from the EIA API. You can set an API key on the [EIA API website](https://www.eia.gov/opendata/). The 

To launch AirFlow locally inside a Docker container with VScode we will use the Dev Containers

To launch AirFlow locally with DockerviaThe Dev Containers settings file `devcontainer.json` is requred to launch the AirFlow webserver and scheduler:


To use this repo setting and trigger the pipeline on AirFlow, you will need an API key for the EIA API. The `devcontainer.json` configuration file loads the EIA API using a local environment variable during the run time using the below settings:

```json
"remoteEnv": {
        "EIA_API_KEY": "${localEnv:EIA_API_KEY}"
    }
```

The API key is set as a local variable named `EIA_API_KEY`, and the `devcontianer.json` loads it as an environment variable. You can obtain the API key via the [EIA API website](https://www.eia.gov/opendata/).



### Launching AirFlow

Once the Dev Containers finished the load process, launch from the terminal the AirFlow webserver:
``` shell
airflow webserver --port 8080
```

Once the process is completed, open a separate terminal and launch the AirFlow scheduler:
```shell
airflow scheduler
```

If the webserver and scheduler were launched successfully, you should access the AirFlow UI from the browser on http://0.0.0.0:8080/.

**Note:** The base image for this POC was built on a Mac machine using Apple Silicon. Therefore, the image may not work on other CPU architectures. 

**TODO:** Create a multi-architecture build


## Dag Settings


The AirFlow dag includes the following steps:
- Initiate MLflow run to track the process
- Check if new data is available on the API
- Refresh the data
- Refresh the forecast (WIP)
- Score the forecast (WIP)

The current 4 dags are based on the DockerOperator using the EIA Forecast POC [image](https://github.com/RamiKrispin/eia-poc/blob/main/.devcontainer/Dockerfile.multiple).


