# Detect and lateralize HS on MRI data

The AID-HS pipeline offers a unique command line to detect and lateralize HS from T1w scan. 

If you wish to use the harmonisation feature of the AID-HS pipeline, you will need to first have computed the harmonisation parameters for the scanner used to acquire the data and used the harmonisation code into the main pipeline command as described bellow. Please refer to our [guidelines to harmonise a new scanner](https://aid-hs.readthedocs.io/en/latest/harmonisation.html). 

Here is the video tutorial about how to run the AID-HS pipeline: [Tutorial on how to run the AID-HS pipeline](https://www.youtube.com/watch?v=VBOdEFMNd2o&t=60s&ab_channel=MELDproject).

## Running

- Ensure you have installed the AID-HS pipeline with [docker container](https://aid-hs.readthedocs.io/en/latest/install_docker.html)
- Ensure you have [organised your data](https://aid-hs.readthedocs.io/en/latest/prepare_data.html) into BIDS format before running this pipeline
- Ensure you have [computed the harmonisation parameters](https://aid-hs.readthedocs.io/en/latest/harmonisation.html) if you want to use the harmonisation parameters 

Open a terminal and `cd` to where you extracted the release zip.

### Running without harmonisation

Ensure "noHarmo" is provided as an harmonisation code for that subject in the `demographics_file` \
Then run:

::::{tab-set}
:::{tab-item} Docker Linux
:sync: Docker Linux

```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -id <subject_id> -demos <demographic_file>
```
:::

:::{tab-item} Docker Windows
:sync: Docker Windows

```bash
docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -id <subject_id> -demos <demographic_file>
```
:::

:::{tab-item} Singularity
:sync: Singularity

First you will need to mount the `aidhs_data_folder` to the `/data` folder of the container by running:
```bash
export APPTAINER_BINDPATH=<path_to_aidhs_data_folder>:/data
```
And then run:
```bash
singularity exec aidhs.sif /bin/bash -c "cd /app && python scripts/new_patient_pipeline/new_patient_pipeline.py -id <subject_id> -demos <demographic_file>"
```

:::
:::{tab-item} Native
:sync: native

```bash
python scripts/new_patient_pipeline/new_patient_pipeline.py -id <subject_id> -demos <demographic_file>
```

:::
::::


### Running with harmonisation
You will need to have computed the harmonisation parameters for that harmonisation code \
Ensure you the same harmonisation code is provided for that subject in the `demographics_file` \
Then run: 

::::{tab-set}

:::{tab-item} Docker Linux
:sync: Docker Linux
```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -id <subject_id> -demos <demographic_file> -harmo_code <harmonisation_code>
```
:::

:::{tab-item} Docker Windows
:sync: Docker Windows
```bash
docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -id <subject_id> -demos <demographic_file> -harmo_code <harmonisation_code>
```
:::

:::{tab-item} Singularity
:sync: Singularity

First you will need to mount the `aidhs_data_folder` to the `/data` folder of the container by running:
```bash
export APPTAINER_BINDPATH=<path_to_aidhs_data_folder>:/data
```
And then run:
```bash
singularity exec aidhs.sif /bin/bash -c "cd /app && python scripts/new_patient_pipeline/new_patient_pipeline.py -id <subject_id> -demos <demographic_file> -harmo_code <harmonisation_code>"
```

:::
:::{tab-item} Native
:sync: native

```bash
python scripts/new_patient_pipeline/new_patient_pipeline.py -id <subject_id> -demos <demographic_file> -harmo_code <harmonisation_code>
```

:::
::::

## Tune the command

You can tune the AID-HS pipeline command using additional variables and flags as detailed bellow:

| **Mandatory variables**         |  Comment | 
|-------|---|
|either ```-id <subject_id>```  |  if you want to run the pipeline on 1 single subject.|  
|or ```-ids <subjects_list>``` |  if you want to run the pipeline on more than 1 subject, you can pass the name of a text file containing the list of subjects. An example 'subjects_list.txt' is provided in the <aidhs_data_folder>. | 
| **Optional variables** |
| ```-harmo_code <harmo_code>```  | provide the harmonisation code if you want to harmonise your data before prediction. This requires to have [computed the harmonisation parameters](https://aid-hs.readthedocs.io/en/latest/harmonisation.html) beforehand. The harmonisation code should start with H, e.g. H1. | 
|```--parallelise``` | use this flag to speed up the segmentation by running HippUnfold on multiple subjects in parallel. |
|```--skip_segmentation``` | use this flag to skips the hippocampal segmentation and features extraction. Usefull if you already have these outputs and you just want to run the preprocessing and the predictions (e.g: after harmonisation) |
|**More advanced variables** | 
|```--debug_mode``` | use this flag to print additional information to debug the code (e.g print the commands, print errors) |


NOTES: 
- Outputs of the pipeline (AID-HS reports) are stored in the folder ```output/predictions_reports/<subject_id>```. See [guidelines on how to interepret the results]() for more details.

## Examples of use case: 

To run the whole prediction pipeline on subject 'test001' without harmonising the data:

::::{tab-set}
:::{tab-item} Docker Linux
:sync: Docker Linux

```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -id sub-test001
```
:::

:::{tab-item} Docker Windows
:sync: Docker Windows

```bash
docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -id sub-test001
```
:::

:::{tab-item} Singularity
:sync: Singularity

```bash
singularity exec aidhs.sif /bin/bash -c "cd /app && python scripts/new_patient_pipeline/new_patient_pipeline.py -id sub-test001"
```

:::
:::{tab-item} Native
:sync: native

```bash
python scripts/new_patient_pipeline/new_patient_pipeline.py -id sub-test001
```

:::
::::

To run the whole prediction pipeline on subject 'test001' using harmonisation code H1:

::::{tab-set}
:::{tab-item} Docker Linux
:sync: Docker Linux

```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -id sub-test001 -harmo_code H1
```
:::

:::{tab-item} Docker Windows
:sync: Docker Windows

```bash
docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -id sub-test001 -harmo_code H1
```
:::

:::{tab-item} Singularity
:sync: Singularity

```bash
singularity exec aidhs.sif /bin/bash -c "cd /app && python scripts/new_patient_pipeline/new_patient_pipeline.py -id sub-test001 -harmo_code H1"
```
:::
:::{tab-item} Native
:sync: native

```bash
python scripts/new_patient_pipeline/new_patient_pipeline.py -id sub-test001 -harmo_code H1
```

:::
::::

To run the whole prediction pipeline on multiples subjects with parallelisation:

::::{tab-set}
:::{tab-item} Docker Linux
:sync: Docker linux
```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -ids list_subjects.txt --parallelise
```
:::

:::{tab-item} Docker Windows
:sync: Docker Windows
```bash
docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -ids list_subjects.txt --parallelise
```
:::

:::{tab-item} Singularity
:sync: Singularity

```bash
singularity exec aidhs.sif /bin/bash -c "cd /app && python scripts/new_patient_pipeline/new_patient_pipeline.py -ids list_subjects.txt --parallelise"
```

:::
:::{tab-item} Native
:sync: native

```bash
python scripts/new_patient_pipeline/new_patient_pipeline.py -ids list_subjects.txt --parallelise
```

:::
::::

## Interpretation of results

Refer to our [guidelines](https://aid-hs.readthedocs.io/en/latest/interpret_results.html) for details on how to read and interprete the AID-HS pipeline results
