import os
from glob import glob
from os.path import join as opj
import subprocess
from subprocess import Popen, DEVNULL, STDOUT, check_call
import multiprocessing
from functools import partial
import shutil
from aidhs.tools_pipeline import get_m


def init(lock):
    global starting
    starting = lock

def prepare_T1_parallel(subjects, num_procs=20):
    # parallel version of the pipeline, finish each stage for all subjects first

    pool = multiprocessing.Pool(processes=num_procs, initializer=init, initargs=[multiprocessing.Lock()])
    for _ in pool.imap_unordered(partial(prepare_T1), subjects):
        pass

def prepare_T1(subject):
   
    subject_id = subject.id
    bids_s = subject.bids_dir

    #check t1 fs file exists
    # t1_s = opj(subject.fs_dir, 'mri', 'T1.mgz') #use T1 from FS dir
    t1_s = subject.t1_input #use raw T1
    if not os.path.isfile(t1_s):
        print(f'ERROR: Could not find the T1 file for subject {subject_id}')
        return
  
    #bidsify 
    if bids_s != None:
        bidsify_results(subject, t1_s, 'T1w')
    else:
        print(f'INFO: no modality T1w found. Skip preparation for this modality')
    
def bidsify_results(subject, file, modality, verbose=False):
    
    print(get_m(f'bidsify {modality} file', subject.id, 'INFO')) 
    # associate new id or clean subject id to be bids compatible
    bids_id = subject.bids_id
    bids_s = subject.bids_dir 

    #create bids directory for subject if does not exist
    if not os.path.isdir(bids_s):  
        os.makedirs(bids_s, exist_ok=True)

    #get files and convert in nifti if needed 
    f_split = file.split('.')
    f_type=f_split[::-1]
    if (modality == 'FA') or (modality == 'MD'):
        type_bids='dwi'
    else:
        type_bids='anat'
    if not os.path.isdir(opj(bids_s, type_bids)):  
        os.makedirs(opj(bids_s, type_bids), exist_ok=True)
    output_file = opj(bids_s, type_bids, bids_id+f'_{modality}.nii.gz')
    if not os.path.isfile(output_file):
        if os.path.isfile(file): 
            if 'nii' in f_type:
                shutil.copy(file, output_file)
            elif 'mgz' in f_type:
                command = format(f"mri_convert --in_type mgz --out_type nii {file} {output_file}")
                print(get_m(f'convert {modality} mgz into nifti and save at {output_file}', subject.id, 'INFO')) 
                proc = Popen(command, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                stdout, stderr= proc.communicate()
                if verbose:
                    print(stdout)
                if proc.returncode==0:
                    return True
                else:
                    print(get_m(f'COMMAND failing : {command} with error {stderr}', subject.id, 'ERROR'))
                    return False
            else:
                print(get_m(f'File type not recognized', subject.id, 'ERROR')) 

        else:
            print(get_m(f'Skip bidsify for {modality}. No modality found in inputs', subject.id, 'INFO')) 
    else:
        print(get_m(f'Skip bidsify for {modality}. Modality already exists at {output_file}', subject.id, 'INFO')) 

def extract_surface_features(subject, output_dir=None, verbose=False):
   
    #initialise
    hippo_s = subject.hippo_dir
    if subject.bids_id != None:   
        subject_id = subject.bids_id
    else:
        subject_id = subject.convert_bids_id()

    #create new directory for subject if does not exist
    if output_dir != None:
        surf_s = opj(output_dir, 'hippunfold', subject_id , 'surf_aidhs')
    else:
        surf_s = opj(hippo_s, 'surf_aidhs')
    
    if not os.path.isdir(surf_s):  
        os.makedirs(surf_s, exist_ok=True)

    for hemi_old in ['L','R']:
        if hemi_old=='L':
            hemi='lh'
        else:
            hemi='rh'
        for label in ['label-hipp', 'label-dentate']:
            #copy features already computed by hippunfold
            print(get_m(f'copy features from hippunfold', subject.id, 'INFO')) 
            for feat in ['gyrification','thickness','curvature']:
                if (label=='label-dentate') & (feat=='thickness'):
                    pass
                else:
                    input_file = opj(hippo_s,'surf', f'{subject_id}_hemi-{hemi_old}_space-T1w_den-0p5mm_{label}_{feat}.shape.gii')
                    if os.path.isfile(input_file):
                        shutil.copy(input_file, opj(surf_s, f'{hemi}.{label}.{feat}.shape.gii'))
                    else:
                        print(get_m(f'Feature {hemi}.{label}.{feat}.shape.gii is missing. Check that HippUnfold has ran properly', subject.id, 'ERROR')) 
                        return False
            #create mean and intrinsic curvature
            print(get_m(f'Create mean and intrinsic curvature', subject.id, 'INFO')) 
            input_file = f'{hippo_s}/surf/{subject_id}_hemi-{hemi_old}_space-T1w_den-0p5mm_{label}_outer.surf.gii'
            if os.path.isfile(input_file):
                #create mean curv
                command = format(
                    f"wb_command -surface-curvature {input_file}  -mean {surf_s}/{hemi}.{label}.mean-curv.shape.gii")
                proc = Popen(command, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                stdout, stderr= proc.communicate()
                if verbose:
                    print(stdout)
                if proc.returncode!=0:
                    print(get_m(f'COMMAND failing : {command} with error {stderr}', subject_id, 'ERROR'))
                    return False

                #create gauss curv
                command = format(
                    f"wb_command -surface-curvature {input_file} -gauss {surf_s}/{hemi}.{label}.gauss-curv.shape.gii")
                proc = Popen(command, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                stdout, stderr= proc.communicate()
                if verbose:
                    print(stdout)
                if proc.returncode!=0:
                    print(get_m(f'COMMAND failing : {command} with error {stderr}', subject_id, 'ERROR'))
                    return False
            
                #filter intrinsic curvature : abs
                command = format(
                    f"wb_command -metric-math 'abs(x)' {surf_s}/{hemi}.{label}.gauss-curv_filtered.shape.gii -var x {surf_s}/{hemi}.{label}.gauss-curv.shape.gii ")
                proc = Popen(command, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                stdout, stderr= proc.communicate()
                if verbose:
                    print(stdout)
                if proc.returncode!=0:
                    print(get_m(f'COMMAND failing : {command} with error {stderr}', subject_id, 'ERROR'))
                    return False
        
                #smooth intrinsic curvature (kernel 10mm) with or without masking of the side
                command = format(
                    f"wb_command -metric-smoothing  {input_file} {surf_s}/{hemi}.{label}.gauss-curv_filtered.shape.gii '1' {surf_s}/{hemi}.{label}.gauss-curv_filtered_sm1.shape.gii")
                proc = Popen(command, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                stdout, stderr= proc.communicate()
                if verbose:
                    print(stdout)
                if proc.returncode!=0:
                    print(get_m(f'COMMAND failing : {command} with error {stderr}', subject_id, 'ERROR'))
                    return False
            

                 
