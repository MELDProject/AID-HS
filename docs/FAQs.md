# Common errors

# FAQs

## **Issues & questions with installation**

### **Issue with the AID-HS License**

- If your issue is:
    ```bash
    ERROR: Could not find a AIDHS_LICENSE environment variable. Please ensure you have exported the AIDHS_LICENSE environment following the AID-HS installation guidelines
    ```
    This means that the AIDHS_LICENSE variable has not been exported/initialised in the environment (terminal) you are using. The variable should be automatically exported when using compose.yml file for the Docker. For native installation, you can export manually the environment variable by doing: 
    ```bash
    export AIDHS_LICENSE=<path_to_aidhs_license_file>
    ```
    Please contact the team if the issue continues

- If your issue is: 
    ```bash
    ERROR: The file aidhs_license.txt does not exist.
    Please ensure you got the AID-HS license file by filling the registration form provided in the AID-HS installation guidelines and provided the right path to the file
    ```
    This means that the aidhs_license.txt cannot be found in the main aidhs folder (where the code is). This can happen if you did not get the AID-HS license file or if the file was placed in an incorect folder. To get the proper AID-HS license ID, please fill in to the [AID-HS registration form](https://docs.google.com/forms/d/e/1FAIpQLSdPbtraBZ2s0HD1W8qtF11wr_fYVTWZjraED03Rtl2ZjxeRMA/viewform?usp=header).

- If your issue is:
    ```bash
    ERROR: The license ID provided does not seem correct.
    Please ensure you got the correct AID-HS license file by filling the registration form provided in the AID-HS installation guidelines and provided the right path to the file
    ```
    or 
    ```bash
    ERROR: The license file aidhs_license.txt does not seem correct.
    Please ensure you got the correct AID-HS license file by filling the registration form provided in the AID-HS installation guidelines and provided the right path to the file

    ```
    This means that the AID-HS license file exists and is at the correct place, but the license ID does not exist or is incorrect. To get the proper AID-HS license ID, please fill in the [AID-HS registration form](https://docs.google.com/forms/d/e/1FAIpQLSdPbtraBZ2s0HD1W8qtF11wr_fYVTWZjraED03Rtl2ZjxeRMA/viewform?usp=header).



### **Issue with Singularity - Not enough space when with creating the SIF**
```bash
INFO:    Creating SIF file... 
FATAL:   While performing build: while creating squashfs: create command failed: exit status 1:  
Write failed because No space left on device 
```
It means there is not enough space where the default singularity/apptainer cache and temporary directories are located. Usually the default cache is located in `$HOME/.singularity/cache` and the default temporary directory `$HOME/.tmp`\
Solution:
- You can make space in the default `$HOME` directory
- You can change the singularity/apptainer cache and temporary directories for a folder where there is space:
    ```bash
    export SINGULARITY_CACHEDIR=<path_folder_with_space> 
    export SINGULARITY_TMPDIR=<path_folder_with_space>
    ```
    Or with apptainer
    ```bash
    export APPTAINER_CACHEDIR=<path_folder_with_space> 
    export APPTAINER_TMPDIR=<path_folder_with_space>
    ```
---

## **Issues & questions with pipeline use**

### **Issue with HippUnfold - HippUnfold segmentation runs until step 37 of 193 steps (19%) and then is killed**

```bash
/bin/bash: line 1:   210 Killed                  nnUNet_predict -i tempimg -o templbl -t Task101_hcp1200_T1w -chk model_best --disable_tta &> logs/sub-0001/sub-0001_hemi-R_space-corobl_nnunet.txt
Shutting down, this might take some time.
Exiting because a job execution failed. Look above for error message

```

The error is likely due to a memory issue when HippUnfold is calling nnUNet to predict.\
If you are using Docker Desktop, it could be because the memory limit is set very low by default. 
To remedy, you will need to:
1) Increase the memory in the Docker Desktop settings (more help in this [post](https://forums.docker.com/t/how-to-increase-memory-size-that-is-available-for-a-docker-container/78483))
2) Delete the hippunfold subject folders below:
    - `output/hippunfold_outputs/hippunfold/<subjectID>`
    - `output/hippunfold_outputs/work/<subjectID>`
3) Run the AID-HS command again. 

### **Warning with Orphans containers**

```bash
WARN[0000] Found orphan containers ([aid-hs-101-aidhs-run-5818580c067f aid-hs-101-aidhs-run-bd51a3643bcb aid-hs-101-aidhs-run-e7a644059fdb aid-hs-101-aidhs-run-90b9a6b2d7e7 aid-hs-101-aidhs-run-109ef780e484 aid-hs-101-aidhs-run-483c2e531ac9 aid-hs-101-aidhs-run-acacca2b2930]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up.
```

This is just a warning and will not impact the use of the pipeline. But to clean up the orphans containers please use the command below: 
```bash
docker-compose down --remove-orphans
```

---

## **Updating AID-HS to V1.1.0**

The instructions below are for users that already have used AID-HS v1.0.1 on patients and would like to update to AID-HS v1.1.0 while keeping the same aidhs_data_folder folder.

### ** Register to get your AID-HS license**:
Register at [AID-HS registration form](https://docs.google.com/forms/d/e/1FAIpQLSdPbtraBZ2s0HD1W8qtF11wr_fYVTWZjraED03Rtl2ZjxeRMA/viewform?usp=header). Following registration you will received a license file. This file will be needed for use of all future AID-HS versions v1.1.0 and above. Your email address will be added to the AID-HS mailing list. This will ensure that we can update you about bugs fix and new releases. 

### 📥 **Get the updated code**

Please follow the Download method below to get the new code

::::{tab-set}

:::{tab-item} Download
1. Go to the [github releases page](https://github.com/AID-HSProject/AID-HS/releases) and download the latest version `V1.1.0`, by clicking on `Source code (zip)` or `Source code (tar.gz)`.
2. Extract the folder `AID-HS-1.1.0`
3. Copy the files below from your old `AID-HS-1.0.1` directory to your new `AID-HS-1.1.0` directory:
    - the `compose.yml`
    - the `config.ini`
4. Copy the `aidhs_license.txt` into the extracted folder (see above how to get the AID-HS license)
:::

:::{tab-item} Git
1) Open a terminal in your `aidhs` folder
2) Pull the latest code from GitHub (it will pull the latest data while keeping your changes made to the code)
```bash
git stash
git pull 
git stash pop
```
3) Copy the `aidhs_license.txt` into the extracted folder (see above how to get the AID-HS license)
:::
::::

Then depending on if you have a Native, Docker or Singularity installation of AID-HS `v1.0.1` you will need to follow the same type of installation to update to `v1.1.0`: 

::::{tab-set}

:::{tab-item} Native
:sync: Native
**💻 Native Installation Users:** Your will need to update your environment with the new code. 

1. Activate your conda environment
```
conda activate aidhs
```
2. Update the code package in the environment. Make sure you are in the new `AID-HS-1.1.0` directory and run:
```
pip install -e . 
```

:::

:::{tab-item} Docker
:sync: Docker

**🐳 Docker Users:** You will need to pull the latest docker image
```bash
docker pull MELDproject/aidhs:latest
```

:::

:::{tab-item} Singularity
:sync: Singularity

**🚀 Singularity Users:** You will need to pull the latest image
```bash
singularity pull docker://MELDproject/aidhs:latest
```
:::
::::

### ✔️ **Run pytest again**
Follow the guidelines **"Verify installation"** to run the test again.
- 💻[Native Installation Users](https://aid-hs.readthedocs.io/en/latest/install_native.html#verify-installation)
- 🐳[Docker Users](https://aid-hs.readthedocs.io/en/latest/install_docker.html#verify-installation)
- 🚀[Singularity Users](https://aid-hs.readthedocs.io/en/latest/install_singularity.html#verify-installation)

### 🧠 **Update your predictions with the harmonisation parameters fix**
If you want to update the predictions with the new registration for patients you have already ran through AID-HS, please follow the instructions bellow:

1) Create a list of ids of patients you want to rerun: e.g. `list_subjects_rerun_v1.1.0.txt`

2) Delete the previous harmonisation parameters and harmonised data found in <aidhs_data_folder>/output/preprocessed_surf_data/AIDHS_<site_code>. And rerun the harmonisation process again. 

2) Then run the prediction pipeline again. It will recreate the PDF report for your patient.

**WARNING** This will overwrite the data for that patient and the patient report in `output/predictions_reports`

::::{tab-set}

:::{tab-item} Native
:sync: Native

**💻 Native Installation Users:** 
```bash
python scripts/new_patient_pipeline/new_patient_pipeline.py -ids list_subjects_rerun_v1.1.0.txt -demos demographics_file.csv
```
:::

:::{tab-item} Docker
:sync: Docker

**🐳 Docker Users:** 
```bash
DOCKER_USER="$(id -u):$(id -g)" docker compose run aidhs python scripts/new_patient_pipeline/new_patient_pipeline.py -ids list_subjects_rerun_v1.1.0.txt -demos demographics_file.csv
```
:::

:::{tab-item} Singularity
:sync: Singularity

**🚀 Singularity Users:**
```bash
singularity exec aidhs.sif /bin/bash -c "cd /app && python scripts/new_patient_pipeline/new_patient_pipeline.py -ids list_subjects_rerun_v1.1.0.txt -demos demographics_file.csv"
```
:::
::::
