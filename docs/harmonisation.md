# Compute the harmonisation parameters for a new scanner

## Information about the harmonisation
The AID-HS pipeline enables the harmonisation of your patient's features before prediction, if you are providing harmonisation parameters.

Harmonisation of your patient data is not mandatory but recommended, to remove any bias induced by the scanner and sequence used, and be able to interprete the normative curves. For more details on the AID-HS performances with and without harmonisation please refers to our [paper](https://onlinelibrary.wiley.com/doi/10.1002/ana.27089?af=R)

Here is the video tutorial about how to run the harmonisation using the AID-HS pipeline: [Tutorial on how to run the harmonisation](https://www.youtube.com/watch?v=drMap14Sm6Y&t=12s&ab_channel=MELDproject).

## Compute the harmonisation paramaters 

The harmonisation parameters are computed using [Distributed Combat](https://doi.org/10.1016/j.neuroimage.2021.118822).
To get these parameters you will need a cohort of subjects acquired from the same scanner and under the same protocol (sequence, parameters, ...).
Subjects can be controls and/or patients, but we advise to use ***at least 20 subjects*** to enable an accurate harmonisation, and to not use HS patients for the harmonisation. 
Try to ensure the data are high quality (i.e no blurring, no artefacts, no cavities in the brain).
Demographic information (e.g age and sex) will be required for this process, follow the [guidelines](https://aid-hs.readthedocs.io/en/latest/prepare_data.html) 

WARNING: zero variance in the demographics information (e.g. having the same age for all subjects) will lead to Combat failures or errors. 

Once you have done the process once, you can follow the [general guidelines to predict on a new patient](https://aid-hs.readthedocs.io/en/latest/run_prediction_pipeline.html) 

## Running

- Ensure you have installed the AID-HS pipeline with [docker container](https://aid-hs.readthedocs.io/en/latest/install_docker.html). 
- **Chose a harmonisation** code for this scanner starting by 'H' (e.g H1, H2, ..). This harmonisation code will be needed to organise your data and run the code as detailled below. 
- Ensure you have [organised your MRI data](https://aid-hs.readthedocs.io/en/latest/prepare_data.html#prepare-the-mri-data-in-bids-format-mandatory) and [provided demographic information](https://aid-hs.readthedocs.io/en/latest/prepare_data.html#prepare-the-demographic-information-to-run-the-harmonisation) before running this pipeline. 


### Second step : Run the pipeline to get the harmonisation parameters

Open a terminal and `cd` to where you extracted the release zip.

::::{tab-set}
:::{tab-item} Docker Linux
:sync: Docker Linux
```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -harmo_code <harmo_code> -ids <subjects_list> -demos <demographic_file> --harmo_only
```
:::

:::{tab-item} Docker Windows
:sync: Docker Windows
```bash
docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -harmo_code <harmo_code> -ids <subjects_list> -demos <demographic_file> --harmo_only
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
singularity exec aidhs.sif /bin/bash -c "cd /app && python scripts/new_patient_pipeline/new_patient_pipeline.py -harmo_code <harmo_code> -ids <subjects_list> -demos <demographic_file> --harmo_only"
```

:::
:::{tab-item} Native
:sync: native

```bash
python scripts/new_patient_pipeline/new_patient_pipeline.py -harmo_code <harmo_code> -ids <subjects_list> -demos <demographic_file> --harmo_only
```

:::
::::

This calls the AID-HS pipeline command. You can tune this command using the variables and flag describes further below. 

Note: This command will segment the hippocampus using HippUnfold, extract the hippocampal features and compute the harmonisation parameters, for the subjects provided in the subjects list. If you wish to also get the predictions on these subjects you can remove the flag '--harmo_only'. 

## Tune the command

You can tune this command using additional variables and flags as detailed bellow:

| **Mandatory variables**         |  Comment | 
|-------|---|
|```-harmo_code <harmo_code>```  |  The site code should start with H, e.g. H1. | 
|```-ids <subjects_list>``` |  A text file containing the list of subjects. An example 'subjects_list.txt' is provided in the <aidhs_data_folder>. | 
|```-demos <demographic_file>```| The name of the csv file containing the demographic information as detailled in the [guidelines](https://aid-hs.readthedocs.io/en/latest/prepare_data.html#prepare-the-mri-data-in-bids-format-mandatory) and [provided demographic information](https://aid-hs.readthedocs.io/en/latest/prepare_data.html#prepare-the-demographic-information-to-run-the-harmonisation). An example 'demographics_file.csv' is provided in the <aidhs_data_folder>.|
| **Optional variables** |
|```--parallelise``` | use this flag to speed up the segmentation by running HippUnfold on multiple subjects in parallel. |
|```--harmo_only``` | Use this flag to do all the processes up to the harmonisation. Usefull if you want to harmonise on some subjects but do not wish to predict on them |


## What's next ? 
Once you have successfully computed the harmonisation parameters, they should be saved in your <aidhs_data_folder>. The file is called 'AIDHS_<site_code>_combat_parameters.hdf5' and is stored in 'output/preprocessed_surf_data/AIDHS_<site_code>/'.
You can now refer to the guidelines [to predict a new patient](https://aid-hs.readthedocs.io/en/latest/run_prediction_pipeline.html) to predict lesion in patients from that same scanner.