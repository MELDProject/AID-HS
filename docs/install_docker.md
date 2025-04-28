# Docker container


**WARNING: Installation and use has not yet been tested on Windows. Please let us know if you have succeeded or are having challenges using the docker container on Windows**

The Docker container has all the prerequisites embedded into it. This makes it easier to install and compatible with most OS systems. 

Notes: 
- Currently only tested on **Linux** (HPC Singularity coming soon)
- You will need **~20GB of space** to install the container
- The docker image contains Miniconda 3, HippUnfold v1.1.0, and AID-HS. The whole image is ~18GB.  

Here is the video tutorial demonstrating how to do the docker installation - [Docker and Singularity Installation of AID-HS Tutorial](https://www.youtube.com/watch?v=RRAET7r05ys&t=11s&ab_channel=MELDproject).

## Prerequisites

### Install Docker
You will need to have docker installed. You can check if docker is installed on your computer by running:

```bash
docker --version
```

If this command displays the docker version then it is already installed. If not, please follow the [guidelines](https://docs.docker.com/engine/install/) to install docker on your machine. Make sure to download the correct version for your OS system!

## Enable GPUs

Enabling your computer's GPUs for running the pipeline accelerates the HippUnfold segmentation . Follow instructions for your operating system to install.

Install the [*nvidia container toolkit*](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

## Installation & configuration
In order to run the docker, you'll need to configure a couple of files

1. Download `aidhs.zip` from the [latest github release](https://github.com/MELDProject/AID-HS/releases/latest) and extract it.
2. Download the aidhs_data_folder at https://figshare.com/s/16011ee4d6b5723b14b6
3. Unzip the folder where you want to store the aidhs_data_folder
4. In the AID-HS folder, open and edit the compose.yml to add the path to the aidhs_data_folder. The initial compose.yml file looks like :
```
services:
  aidhs:
    image: meldproject/aidhs:latest
    platform: "linux/amd64"
    volumes:
      - volumes:/data
    user: $DOCKER_USER
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
              count: 0

```
Change the line below "`volumes:`" to point to the aidhs_data_folder. Do not delete the "`:/data`" at the end.\
For example, if you wanted the folder to be on a mounted drive such as "`/mnt/datadrive/aidhs-data`" you should change the line as showed below:

```
    volumes:
      - /mnt/datadrive/aidhs-data:/data
```

:::{admonition} Windows
:class: tip

On windows, if you're using absolute paths, use forward slashes and quotes:
```
    volumes:
      - "C:/Users/John/Desktop/meld-data:/data"
```
:::


5. **WARNING:** If you do not have GPU on your computer (e.g. Mac laptop) you will need to open the compose.yml file and remove the last 6th lines of the text (everything that includes `deploy` and below).\
Your file should look like that: 
```
services:
  aidhs:
    image: meldproject/aidhs:latest
    platform: "linux/amd64"
    volumes:
      - volumes:/data
    user: $DOCKER_USER
```

6. **WARNING** If you are running docker with Docker Desktop, you will need to ensure that the memory usage allowed by docker is to the maximum, as  Docker Desktop halves the memory usage by default. For that you can go in the Docker Desktop settings and change the memory limit (more help in this [post](https://stackoverflow.com/questions/43460770/docker-windows-container-memory-limit))

## Download AID-HS docker & Verify installation
The line below will download AID-HS and then run a test to verify that everything is installed and set up properly. It may take up to an 1h to download the docker image and then takes approximately 1 minute to run the test.

::::{tab-set}

:::{tab-item} Linux
:sync: linux
```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs pytest
```
:::

:::{tab-item} Windows
:sync: windows
```bash
docker compose run aidhs pytest
```
:::

::::

### Errors

If you run into errors during the downloading of the AID-HS docker, contact us by email with information about the package you are trying to install, your OS system and a screenshot of the error you encountered. [How best to reach us.](#contact)

If the installation seems to have worked but you are running into errors during the test you can re-run the test above by changing the last line of the command by the command below to save the terminal outputs in a txt file. Please send `pytest_errors.log` to us so we can work with you to solve any problems. [How best to reach us.](#contact)

::::{tab-set}

:::{tab-item} Linux
:sync: linux
```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs pytest -s | tee pytest_errors.log
```
:::

:::{tab-item} Windows
:sync: windows
```bash
docker compose run aidhs pytest -s | tee pytest_errors.log
```
:::

::::

You will find `pytest_errors.log` in the folder where you launched the command. 

## Test GPU

If you have GPU available, you can test that the pipeline is working well with your GPU by changing `count` to `all` in the `compose.yml` file. The `deploy` section should look like this to enable gpus:

```
deploy:
  resources:
    reservations:
      devices:
        - capabilities: [gpu]
          count: all
```

To disable gpus, change it back to `0`.

Note: if you don't have GPUs on your computer you should remove the lines aboves from the compose.yml file

## FAQs
Please see our [FAQs](https://aid-hs.readthedocs.io/en/latest/FAQ.html) for common installation problems.

## Contact

If you encounter any errors, please contact `m.ripart@ucl.ac.uk` for support
