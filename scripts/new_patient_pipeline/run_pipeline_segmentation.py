import os
import sys
import argparse
import numpy as np
from glob import glob
from os.path import join as opj
import pandas as pd
import json
import bids.layout

from aidhs.tools_pipeline import get_m
from scripts.preprocess.run_script_segmentation import run_hippunfold_parallel, run_hippunfold
from scripts.preprocess.run_script_dataprep import prepare_T1_parallel ,prepare_T1, extract_surface_features
from aidhs.paths import DATA_PATH, FS_SUBJECTS_PATH, HIPPUNFOLD_SUBJECTS_PATH, BIDS_SUBJECTS_PATH

def init(lock):
    global starting
    starting = lock

class SubjectSeg:
    def __init__(self, subject_id, input_dir=None, fs_dir=None, bids_dir=None, hippo_dir=None, bids_id=None):
        
        #initialise
        self.id=subject_id
        
        #update bids id
        self.bids_id = self.convert_bids_id(bids_id=bids_id)
        
        #update directories
        self.get_input_dir(input_dir)
        self.get_fs_dir(fs_dir)
        self.get_bids_dir(bids_dir)
        self.get_hippo_dir(hippo_dir)
   
        #update inputs path 
        if self.input_dir!=None:
           self.t1_input = self.get_inputs_volumes_path(modality='T1', input_dir=input_dir)
           
        #update bids path
        if self.bids_dir!=None:
           self.t1_bids = self.get_bids_volumes_path(modality='T1w', bids_dir=bids_dir)


    #functions
    # update id with bids compatible
    def convert_bids_id(self, bids_id=None):
        if bids_id == None:
            bids_id = self.id
        #clean id
        list_exclude = ['{','}','_']
        for l in list_exclude:
            if l in bids_id:
                bids_id = bids_id.replace(l, '')
        #add 'sub' if needed  
        if not 'sub-' in bids_id:
            bids_id = 'sub-'+bids_id
        print(f'INFO: subject {self.id} converted in {bids_id}')
        #TODO: write in a csv new id and old id?
        self.bids_id = bids_id
        return self.bids_id
    
    #update with input directory
    def get_input_dir(self, input_dir):
        if input_dir != None:
            self.input_dir = opj(input_dir, self.id)
        else:
            print('WARNING: no input directory provided or existing')
            self.input_dir = None
        return self.input_dir

    #update with FS directory
    def get_fs_dir(self, fs_dir):
        if fs_dir != None:
            self.fs_dir = opj(fs_dir, self.id)
        else:
            print('WARNING: subject_input_dirory')
    def get_bids_dir(self, bids_dir, bids_id=None):
        if bids_id ==  None:
            bids_id = self.id
        if bids_dir != None:
            self.bids_dir = opj(bids_dir, bids_id)
        else:
            print('WARNING: no BIDS directory provided or existing')
            self.bids_dir = None
        return self.bids_dir

    #update with hippunfold directory
    def get_hippo_dir(self, hippo_dir):
        if hippo_dir != None:
            self.hippo_dir = opj(hippo_dir, 'hippunfold', self.bids_id)   
        else:
            print('WARNING: no hippunfold directory provided or existing')
            self.hippo_dir = None
        return self.hippo_dir

    #find inputs volumes paths
    def get_inputs_volumes_path(self, modality='T1',input_dir=None):
        '''Find input volume in BIDS or MELD format'''
        if input_dir == None :
            input_dir= self.input_dir
        if input_dir == None:
            print(f'ERROR: No input directory provided to find {modality} volume')
            return
        if not os.path.isdir(input_dir):
            print(f'ERROR: Input directory provided does not exist at {input_dir}')
            return
        
        subject_input_dir= self.get_input_dir(input_dir)
        #look if MELD format
        subject_path = glob(os.path.join(subject_input_dir, modality, "*.nii*"))
        if len(subject_path) > 1:
            raise FileNotFoundError(
                f"Find too much volumes for {modality}. Check and remove the additional volumes with same key name"
            )
        elif not subject_path:
            subject_path = None
        else:
            subject_path = subject_path[0]
        
        # look if BIDS format
        if subject_path == None:
            # get bids structure
            layout = bids.layout.BIDSLayout(input_dir)
            # find parameters to extract bids file
            config_file = os.path.join(input_dir, 'bids_config.json')
            with open(config_file, "r") as json_file:
                dict = json.load(json_file)
            # Create query
            query = dict[modality]
            query['subject'] = self.id.split('sub-')[-1]
            # Get a list of matching files
            subject_path = layout.get(return_type='file', extension=['nii.gz'], **query)
            if len(subject_path) > 1:
                raise FileNotFoundError(
                f"Find too much volumes for {modality}. Check and remove the additional volumes with same key name"
                )
            elif not subject_path:
                print(f"No {modality} file has been found for {self.id}")
                subject_path = 'None'
            else:
                subject_path = subject_path[0]
        return subject_path

    #find bids volumes paths
    def get_bids_volumes_path(self, modality='T1w',bids_dir=None):
        if bids_dir == None :
            bids_dir= self.bids_dir
        if bids_dir == None:
            print(f'ERROR: No input directory provided to find {modality} volume')
            return
        bids_id = self.bids_id
        subject_bids_dir= self.get_bids_dir(bids_dir, bids_id)
        #define file
        if modality=='DTI':
            mod_type='dwi'
        else:
            mod_type='anat'
        subject_path = opj(subject_bids_dir, mod_type, f'{bids_id}_{modality}.nii.gz')
        return subject_path

def run_pipeline_segmentation(list_ids=None, sub_id=None, input_dir=None, fs_dir=None, bids_dir=None, hippo_dir=None, 
                use_parallel=False, skip_fs=False, verbose=False):
    subject_id=None
    subject_ids=None
    if list_ids != None:
        list_ids=os.path.join(DATA_PATH, list_ids)
        try:
            sub_list_df=pd.read_csv(list_ids)
            subject_ids=np.array(sub_list_df.ID.values)
            try: 
                subject_bids_ids=np.array(sub_list_df.bids_ID.values)
            except:
                subject_bids_ids=np.full(len(subject_ids), None)
        except:
            subject_ids=np.array(np.loadtxt(list_ids, dtype='str', ndmin=1)) 
            subject_bids_ids=np.full(len(subject_ids), None)            
    elif sub_id != None:
        subject_id=sub_id
        subject_ids=np.array([sub_id])
        subject_bids_ids=np.full(len(subject_ids), None) 
    else:
        print('ERROR: No ids were provided')
        print("ERROR: Please specify subject(s) ...")
        sys.exit(-1) 
  
    subjects=[]
    for i, subject_id in enumerate(np.array(subject_ids)):
        subjects.append(SubjectSeg(subject_id, input_dir=input_dir, fs_dir=fs_dir, bids_dir=bids_dir, hippo_dir=hippo_dir, bids_id=subject_bids_ids[i]))
    
    subject_ids_failed=[]

    if use_parallel:
        #launch segmentation and feature extraction in parallel
        print(get_m(f'Run subjects in parallel', None, 'INFO'))   
        # prepare T1
        print(get_m(f'STEP 2a: Prepare T1 for hippunfold', None, 'INFO'))
        prepare_T1_parallel(subjects)
        # extract surface based features
        print(get_m(f'STEP 2b: Run hippunfold segmentation', None, 'INFO'))
        result = run_hippunfold_parallel(subjects, bids_dir=bids_dir, hippo_dir=hippo_dir, verbose=verbose)
        if result == False:
            print(get_m(f'One step of the pipeline has failed. Process has been aborted for one subject', None, 'ERROR'))
            return False
        print(get_m(f'STEP 3: Extract hippocampal surface features', None, 'INFO')) 
        subject_ids_failed =[]
        for subject in subjects:
            result = extract_surface_features(subject, output_dir=hippo_dir, verbose=verbose)
            if result == False:
                subject_ids_failed.append(subject.id)
    else:
        #launch segmentation and feature extraction for each subject one after another
        print(get_m(f'No parralelisation. Run subjects one after another', None, 'INFO')) 
        for subject in subjects:
            result = True
            #prepare T1
            print(get_m(f'STEP 2a: Prepare T1 for hippunfold', subject.id, 'INFO'))
            result = prepare_T1(subject)
            if result == False:
                subject_ids_failed.append(subject.id)
                continue
            #run hippunfold segmentation
            print(get_m(f'STEP 2b: Run hippunfold segmentation', subject.id, 'INFO'))
            result = run_hippunfold(subject, bids_dir=bids_dir, hippo_dir=hippo_dir)
            if result == False:
                subject_ids_failed.append(subject.id)
                continue
            #extract surface based features
            print(get_m(f'STEP 3: Extract hippocampal surface features', subject.id, 'INFO'))
            result = extract_surface_features(subject, output_dir=hippo_dir)
            if result == False:
                subject_ids_failed.append(subject.id)
                continue
        
    if len(subject_ids_failed):
        print(get_m(f'One step of the pipeline has failed. Process has been aborted for subjects {subject_ids_failed}', None, 'ERROR'))
        return False 

if __name__ == "__main__":
    # parse commandline arguments
    parser = argparse.ArgumentParser(description="perform cortical parcellation using recon-all from freesurfer")
    parser.add_argument("-id","--id",
                        help="Subject ID.",
                        default=None,
                        required=False,
                        )
    parser.add_argument("-ids","--list_ids",
                        default=None,
                        help="File containing list of ids. Can be txt or csv with 'ID' column",
                        required=False,
                        )
    parser.add_argument("--parallelise", 
                        help="parallelise segmentation", 
                        required=False,
                        default=False,
                        action="store_true",
                        )
    parser.add_argument("--skip_fs", 
                        help="skip the segmentation with freesurfer", 
                        required=False, 
                        default=False,
                        action="store_true",
                        )
    
    args = parser.parse_args()
    print(args)

    # initialise folders
    data_dir = DATA_PATH
    input_dir = os.path.join(data_dir, 'input')
    fs_dir = FS_SUBJECTS_PATH
    hippo_dir = HIPPUNFOLD_SUBJECTS_PATH
    bids_dir = BIDS_SUBJECTS_PATH

    # initialise parameters
    use_fastsurfer = True
    
    run_pipeline_segmentation(list_ids=args.list_ids,
                sub_id=args.id, 
                input_dir=input_dir,
                fs_dir=fs_dir,
                bids_dir=bids_dir,
                hippo_dir=hippo_dir, 
                use_parallel=args.parallelise, 
                skip_fs=args.skip_fs,
                verbose=False,
                        )



    
