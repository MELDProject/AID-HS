import os
from glob import glob
from os.path import join as opj
import subprocess
from subprocess import Popen
from aidhs.tools_pipeline import get_m

def init(lock):
    global starting
    starting = lock

def check_FS_outputs(folder):
    fname = opj(folder,'stats',f'aparc.DKTatlas+aseg.deep.volume.stats')
    if not os.path.isfile(fname):
        return False
    else:
        return True

def run_hippunfold_parallel(subjects, bids_dir=None, hippo_dir=None, num_procs=10, verbose=False):
    # parallel version of Hippunfold

    #make a directory for the outputs
    os.makedirs(hippo_dir, exist_ok=True)

    subjects_to_run = []
    for subject in subjects:
        hippo_s = subject.hippo_dir
        subject_bids_id = subject.bids_id

        if subject_bids_id != None:
            subject_id = subject_bids_id
        else:
            subject_id = subject.convert_bids_id()
        # subject_id = subject_id.split('sub-')[-1]

        #check if outputs already exists
        files_surf = glob(f'{hippo_s}/surf/*_den-0p5mm_label-hipp_*.surf.gii')

        if files_surf==[]:
            subjects_to_run.append(subject_id)
        else:
            print(get_m(f'Hippunfold outputs already exists. Hippunfold will be skipped', subject_id, 'INFO'))
    
    if subjects_to_run!=[]:
        print(get_m(f'Start Hippunfold segmentation in parallel for {subjects_to_run}', None, 'INFO'))
        command =  format(f"hippunfold {bids_dir} {hippo_dir} participant --participant-label {' '.join(subjects_to_run)} --core {num_procs} --modality T1w")
        if verbose:
            print(command)
        proc = Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        stdout, stderr= proc.communicate()
        if verbose:
            print(stdout)
        if proc.returncode==0:
            print(get_m(f'Finished hippunfold segmentation for {subjects_to_run}', None, 'INFO'))
            return True
        else:
            print(get_m(f'Hippunfold segmentation failed for 1 of the subject. Please check the logs at {hippo_dir}/logs/<subject_id>', None, 'ERROR'))
            print(get_m(f'COMMAND failing : {command} with error {stderr}', None, 'ERROR'))
            return False

def run_hippunfold(subject, bids_dir=None, hippo_dir=None, verbose=False):

    hippo_s = subject.hippo_dir
    subject_bids_id = subject.bids_id

    if subject_bids_id != None:
        subject_id = subject_bids_id
    else:
        subject_id = subject.convert_bids_id()

    #make a directory for the outputs
    os.makedirs(hippo_dir, exist_ok=True)

    #check if outputs already exists
    files_surf = glob(f'{hippo_s}/surf/*_den-0p5mm_label-hipp_*.surf.gii')
    if files_surf==[]:
        print(get_m(f'Start Hippunfold segmentation', subject_id, 'INFO'))
        command =  format(f"hippunfold {bids_dir} {hippo_dir} participant --participant-label {subject_id.split('sub-')[-1]} --core 3 --modality T1w")
        if verbose:
            print(command)
        proc = Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        stdout, stderr= proc.communicate()
        if verbose:
            print(stdout)
        if proc.returncode==0:
            print(get_m(f'Finished hippunfold segmentation', subject_id, 'INFO'))
            return True
        else:
            print(get_m(f'Hippunfold segmentation failed. Please check the log at {hippo_dir}/logs/{subject_id}', subject_id, 'ERROR'))
            print(get_m(f'COMMAND failing : {command} with error {stderr}', subject_id, 'ERROR'))
            return False
    else:
        print(get_m(f'Hippunfold outputs already exists. Hippunfold will be skipped', subject_id, 'INFO'))
    

    

    
