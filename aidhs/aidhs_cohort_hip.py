import sys
from contextlib import contextmanager
from aidhs.paths import (
    DEMOGRAPHIC_FEATURES_FILE,
    SURFACE_UNFOLD_FILE,
    SURFACE_FOLD_FILE,
    SURFACE_UNFOLD_DENTATE_FILE,
    SURFACE_FOLD_DENTATE_FILE,
    DEFAULT_HDF5_FILE_ROOT,
    SUBFIELDS_LABEL_FILE,
    HBT_LABEL_FILE,
    HIPPO_MASK_FILE,
    DENTATE_MASK_FILE,
    NVERT_HIPP,
    NVERT_DG,
    NVERT_AVG,
    BASE_PATH,
)
import pandas as pd
import numpy as np
import nibabel as nb
import os
import glob
import logging
import aidhs.mesh_tools as mt
import scipy
import h5py
from matplotlib.colors import ListedColormap


class AidhsCohort:
    def __init__(self, hdf5_file_root=DEFAULT_HDF5_FILE_ROOT, dataset=None, data_dir=BASE_PATH):
        self.data_dir = data_dir
        self.hdf5_file_root = hdf5_file_root
        self.dataset = dataset
        self.log = logging.getLogger(__name__)

        # class properties (readonly attributes):
        # full_feature_list: list of features available in this cohort
        self._full_feature_list = None

        # cortex_label: information about which nodes are cortex
        self._cortex_label = None
        self._hippo_mask = None
        self._dentate_mask = None
        self._avg_mask = None
        # surf: inflated flat mesh, surface vertices and triangles
        self._surf = None
        self._surf_dentate = None
        # surf_fold: inflated fold mesh, surface vertices and triangles
        self._surf_fold=None
        self._surf_fold_dentate=None
        # surf_partial: partially inflated mesh, surface vertices and triangles
        self._surf_partial = None
        # surf_area: surface area for each triangle
        self._surf_area = None
        # adj_mat: sparse adjacency matrix for all vertices
        self._adj_mat = None
        # lobes: labels for cortical lobes
        self._lobes = None
        # neighbours: list of neighbours for each vertex
        self._neighbours = None
        self._neighbours_dentate = None
        #subfield_label = array with labels of subfields
        self._subfields_labels = None
        #subfield_names = dictionary with subfields name
        self._subfields_names = None
        #subfield_cmap = cmap color for hippo subfields
        self._subfields_cmap = None
        #subfield_atlas = dictionary of hippocampal subfields label and color
        self._subfields_atlas = None
        
        #HBT_label = array with Head-Body-Tail labels
        self._HBT_labels = None
        #HBT_names = dictionary with Head-Body-Tail name
        self._HBT_names = None
        #subfield_cmap = cmap color for hippo subfields
        self._HBT_cmap = None
        #subfield_atlas = dictionary of hippocampal subfields label and color
        self._HBT_atlas = None
        

    @property
    def full_feature_list(self):
        """list of features available in this cohort"""
        if self._full_feature_list is None:
            self._full_feature_list = []
            subject_ids = self.get_subject_ids()
            # get union of all features from subjects in this cohort
            features = set()
            for subj in subject_ids:
                features = features.union(AidhsSubject(subj, self).get_feature_list().copy())
            self._full_feature_list = sorted(list(features))
            self.log.info(f"full_feature_list: {self._full_feature_list}")
        return self._full_feature_list


    def load_gii_surf(self, filename):
        """ import gii file using nibabel. returns flattened data array"""
        gii_file=nb.load(filename)
        vertices= gii_file.agg_data('pointset')
        faces = gii_file.agg_data('triangle')
        return {"faces": faces, "coords": vertices}
    
    def load_gii_shape(self, filename):
        """ import gii file using nibabel. returns flattened data array"""
        gii_file=nb.load(filename)
        mmap_data=gii_file.darrays[0].data
        array_data=np.ndarray.flatten(mmap_data)
        return array_data
    
    @property
    def hippo_mask(self):
        if self._hippo_mask is None:
            p = HIPPO_MASK_FILE
            self._hippo_mask = self.load_gii_shape(p).astype(bool)
        return self._hippo_mask

    @property
    def dentate_mask(self):
        if self._dentate_mask is None:
            p = DENTATE_MASK_FILE
            self._dentate_mask = self.load_gii_shape(p).astype(bool)
        return self._dentate_mask

    @property
    def avg_mask(self):
        if self._avg_mask is None:
            self._avg_mask = np.ones(NVERT_AVG).astype(bool)
        return self._avg_mask

    @property
    def surf_fold(self):
        """inflated surface, dict with 'faces' and 'coords'"""
        if self._surf_fold is None:
            p = SURFACE_FOLD_FILE
            self._surf_fold = self.load_gii_surf(p)
        return self._surf_fold
    
    @property
    def surf(self):
        """flated surface, dict with 'faces' and 'coords'"""
        if self._surf is None:
            p = SURFACE_UNFOLD_FILE
            self._surf = self.load_gii_surf(p)
        return self._surf
    
    @property
    def surf_fold_dentate(self):
        """inflated surface, dict with 'faces' and 'coords'"""
        if self._surf_fold_dentate is None:
            p = SURFACE_FOLD_DENTATE_FILE
            self._surf_fold_dentate = self.load_gii_surf(p)
        return self._surf_fold_dentate

    @property
    def surf_dentate(self):
        """flated surface, dict with 'faces' and 'coords'"""
        if self._surf_dentate is None:
            p =  SURFACE_UNFOLD_DENTATE_FILE
            self._surf_dentate = self.load_gii_surf(p)
        return self._surf_dentate
    
    @property
    def subfields_labels(self):
        """dictionary with hippo subfields and cmap'"""
        if self._subfields_labels is None:
            p =  SUBFIELDS_LABEL_FILE
            self._subfields_labels = nb.load(p).darrays[0].data  
        return self._subfields_labels
    
    @property
    def subfields_names(self):
        """names of subfields'"""
        if self._subfields_names is None: 
            self._subfields_names = {'Sub':1, 'CA1':2, 'CA2':3, 'CA3':4, 'CA4':5}
        return self._subfields_names
    
    @property
    def subfields_atlas(self):
        """dictionary with hippo subfields and cmap'"""
        if self._subfields_atlas is None:
            labels = self.subfields_labels
            subfields=list(set(labels))
            # create colors map
            colors = [[1,0,0,0], [0,1,0,0], [0,0,1,0],  [1,1,0,0], [1,0,1,0]]
            self._subfields_atlas = dict(zip(subfields, colors))  #colors for each labels (optional)
        return self._subfields_atlas
    
    @property
    def subfields_cmap(self):
        """dictionary with hippo subfields and cmap'"""
        if self._subfields_cmap is None:
            self._subfields_cmap = ListedColormap(['red', 'lime', 'blue', 'gold', 'fuchsia'])
        return self._subfields_cmap
    
    @property
    def HBT_names(self):
        """Head-Body-Tail name'"""
        if self._HBT_names is None: 
            self._HBT_names =  {1:'tail', 2:'body', 3:'head'}
        return self._HBT_names

    @property
    def HBT_labels(self):
        """array with with Head Body Tail labels'"""
        if self._HBT_labels is None:
            p = HBT_LABEL_FILE
            self._HBT_labels = nb.load(p).darrays[0].data  
        return self._HBT_labels
       
    @property
    def HBT_atlas(self):
        """dictionary with hippo subfields and cmap'"""
        if self._HBT_atlas is None:
            labels = self.HBT_labels
            subfields=list(set(labels))
            # create colors map
            colors = [[1,0,0,0], [0,1,0,0], [0,0,1,0]]
            self._HBT_atlas = dict(zip(subfields, colors))  #colors for each labels (optional)
        return self._HBT_atlas
    
    @property
    def HBT_cmap(self):
        """dictionary with hippo subfields and cmap'"""
        if self._HBT_cmap is None:
            self._HBT_cmap = ListedColormap(['midnightblue', 'teal', 'gold'])
        return self._HBT_cmap
    
    @property
    def neighbours(self):
        if self._neighbours is None:
            self._neighbours = mt.get_neighbours_from_tris(self.surf["faces"])
        return self._neighbours
    
    @property
    def neighbours_dentate(self):
        if self._neighbours_dentate is None:
            self._neighbours_dentate = mt.get_neighbours_from_tris(self.surf_dentate["faces"])
        return self._neighbours_dentate

    def read_subject_ids_from_dataset(self):
        """Read subject ids from the dataset csv file.
        Returns subject_ids, trainval_ids, test_ids"""
        assert self.dataset is not None, "please set a valid dataset csv file"
        df = pd.read_csv(os.path.join(self.data_dir, self.dataset))
        subject_ids = list(df.subject_id)
        trainval_ids = list(df[df.split == "trainval"].subject_id)
        test_ids = list(df[df.split == "test"].subject_id)
        return subject_ids, trainval_ids, test_ids

    def get_sites(self):
        """get all valid site codes that exist on this system"""
        sites = []
        for f in glob.glob(os.path.join(self.data_dir, "AIDHS_*")):
            if os.path.isdir(f):
                sites.append(f.split("_")[-1])
        return sites

    @contextmanager
    def _site_hdf5(self, site_code, group, write=False, hdf5_file_root=None):
        """
        Hdf5 file handle for specified site_code and group (patient or control).

        This function is to be used in a context block as follows:
        ```
            with cohort._site_hdf5('H1', 'patient') as f:
                # read information from f
                pass
            # f is automatically closed outside of the `with` block
        ```

        Args:
            site_code: hospital site code, e.g. 'H1'
            group: 'patient' or 'control'
            write (optional): flag to open hdf5 file with writing permissions, or to create
                the hdf5 if it does not exist.

        Yields: a pointer to the opened hdf5 file.
        """
        if hdf5_file_root is None:
            hdf5_file_root = self.hdf5_file_root
        p = os.path.join(self.data_dir, 'AIDHS_'+site_code, hdf5_file_root.format(site_code=site_code, group=group))
        # open existing file or create new one
        if os.path.isfile(p) and not write:
            f = h5py.File(p, "r")
        elif os.path.isfile(p) and write:
            f = h5py.File(p, "r+")
        elif not os.path.isfile(p) and write:
            f = h5py.File(p, "a")
        else:
            f = None
        try:
            yield f
        finally:
            if f is not None:
                f.close()

    def get_subject_ids(self, **kwargs):
        """Output list of subject_ids.

        List can be filtered by sites (given as list of site_codes, e.g. 'H2'),
        groups (patient / control / both), features (subject_features_to_exclude),


        Sites are given as a list of site_codes (e.g. 'H2').
        Optionally filter subjects by group (patient or control).
        If self.dataset is not none, restrict subjects to subjects in dataset csv file.
        subject_features_to_exclude: exclude subjects that dont have this feature

        Args:
            site_codes (list of str): hospital site codes, e.g. ['H1'].
            group (str): 'patient', 'control', or 'both'.
            subject_features_to_exclude (list of str): exclude subjects that dont have this feature
            scanners (list of str): list of scanners to include
            lesional_only (bool): filter out lesion negative patients

        Returns:
            subject_ids: the list of subject ids
        """
        # parse kwargs:
        # get groups
        if kwargs.get("group", "both") == "both":
            groups = ["patient", "control"]
        else:
            groups = [kwargs.get("group", "both")]
        # get sites
        site_codes = kwargs.get("site_codes", self.get_sites())
        if isinstance(site_codes, str):
            site_codes = [site_codes]
        # get scanners
        scanners = kwargs.get("scanners", ["3T", "15T", "XT"])
        if not isinstance(scanners, list):
            scanners = [scanners]

        lesional_only = kwargs.get("lesional_only", True)
        subject_features_to_exclude = kwargs.get("subject_features_to_exclude", [""])

        # get subjects for specified groups and sites
        subject_ids = []
        for site_code in site_codes:
            for group in groups:
                with self._site_hdf5(site_code, group) as f:
                    if f is None:
                        continue
                    cur_scanners = f[site_code].keys()
                    for scanner in cur_scanners:
                        subject_ids += list(f[os.path.join(site_code, scanner, group)].keys())

        self.log.info(f"total number of subjects: {len(subject_ids)}")

        # restrict to ids in dataset (if specified)
        if self.dataset is not None:
            subjects_in_dataset, _, _ = self.read_subject_ids_from_dataset()
            subject_ids = list(np.array(subject_ids)[np.in1d(subject_ids, subjects_in_dataset)])
            self.log.info(
                f"total number of subjects after restricting to subjects from {self.dataset}: {len(subject_ids)}"
            )

        # get list of features that is used to filter subjects
        # e.g. use this to filter subjects without FLAIR features
        _, required_subject_features = self._filter_features(
            subject_features_to_exclude,
            return_excluded=True,
        )
        self.log.debug("selecting subjects that have features: {}".format(required_subject_features))

        # filter ids by scanner, features and whether they have lesions.
        # TODO Might want to add eg histology here or other demographic filters.
        filtered_subject_ids = []
        for subject_id in subject_ids:
            subj = AidhsSubject(subject_id, self)
            # check scanner
            if subj.scanner not in scanners:
                continue
            # check required features
            if not subj.has_features(required_subject_features):
                continue
            # check lesion mask presence
            if lesional_only and subj.is_patient and not subj.has_lesion():
                continue
            # subject has passed all filters, add to list
            filtered_subject_ids.append(subject_id)

        self.log.info(
            f"total number after filtering by scanner {scanners}, features, lesional_only {lesional_only}: {len(filtered_subject_ids)}"
        )
        return filtered_subject_ids

    def get_features(self, features_to_exclude=[""]):
        """
        get filtered list of features.
        """
        # get list of all features that we want to train models on
        # if a subject does not have a feature, 0 is returned for this feature during dataset creation
        features = self._filter_features(features_to_exclude=features_to_exclude)
        self.log.debug("features that will be loaded in train/test datasets: {}".format(features))
        return features

    def _filter_features(self, features_to_exclude, return_excluded=False):
        """Return a list of features, with features_to_exclude removed.

        Args:
            features_to_exclude (list of str): list of features that should be excluded,
                NB 'FLAIR' will exclude all FLAIR features but all other features must be exact matches
            return_excluded (bool): if True, return list of excluded features.

        Returns:
            tuple:
                features: the list of features with appropriate features excluded.
                excluded_features: list of all excluded features. Only returned, if return_exluded is specified.
        """

        all_features = self.full_feature_list.copy()
        excludable_features = []
        filtered_features = self.full_feature_list.copy()
        for feature in self.full_feature_list.copy():
            for exclude in features_to_exclude:
                if exclude == "":
                    pass
                elif exclude == "FLAIR":
                    if exclude in feature:
                        filtered_features.remove(feature)
                        excludable_features.append(feature)

                elif feature == exclude:
                    if exclude in self.full_feature_list:  # only remove if still in list
                        filtered_features.remove(feature)
                        excludable_features.append(feature)
        if return_excluded:
            return filtered_features, excludable_features
        else:
            return filtered_features

class AidhsSubject:
    """
    individual patient from aidhs cohort, can read subject data and other info
    """

    def __init__(self, subject_id, cohort):
        self.subject_id = subject_id
        self.cohort = cohort
        self.log = logging.getLogger(__name__)
        # unseeded rng for generating random numbers
        self.rng = np.random.default_rng()

    #adapted for hippo
    @property
    def scanner(self):
        # Note: no need to specify scanner strength with AIDHS pipeline, but still need it to be compatible with previous AIDHS dataset
        scanner = self.get_demographic_features('Scanner')
        if scanner is None:
            scanner="XT" #no need to specify
        if scanner in ("15T" , "1.5T" , "15t" , "1.5t" ):
            scanner="15T" # to be compatible with old way
        elif scanner in ("3T" , "3t" ):
            scanner="3T" # to be compatible with old way
        else:
            scanner="XT" #no need to specify 
        return scanner
    
    #adapted for hippo
    @property
    def group(self):
        group = self.get_demographic_features('Group')
        if (group != "patient") and (group != "control") :
            print(
                f"Error: incorrect group for {self.subject_id}. Unable to determine if patient or control."
            )
            sys.exit()
        return group
    
    #adapted for hippo
    @property
    def site_code(self):
        site_code = self.get_demographic_features('Harmo code', csv_file=DEMOGRAPHIC_FEATURES_FILE)
        return site_code  

    def surf_dir_path(self, hemi):
        """return path to features dir (surf_dir)"""
        return os.path.join(self.site_code, self.scanner, self.group, self.subject_id, hemi)

    def find_path(self, name):
         """ Find the first object with the subject id in the hdf5"""
         if self.subject_id in name:
             return name 
         
    @property
    def is_patient(self):
        return self.group == "patient"

    @property
    def has_flair(self):
        return "FLAIR" in " ".join(self.get_feature_list())

    def has_lesion(self):
        return self.get_lesion_hemisphere() in ["lh", "rh"]

    def get_lesion_hemisphere(self):
        """
        return 'lh', 'rh', or None
        """
        if not self.is_patient:
            return None

        with self.cohort._site_hdf5(self.site_code, self.group) as f:
            surf_dir_lh = f[os.path.join(self.site_code, f[self.site_code].visit(self.find_path), "lh")]
            if ".on_lh.lesion.mgh" in surf_dir_lh.keys():
                return "lh"
            surf_dir_rh = f[os.path.join(self.site_code, f[self.site_code].visit(self.find_path), "rh")]
            if ".on_lh.lesion.mgh" in surf_dir_rh.keys():
                return "rh"
        return None

    def has_features(self, features):
        missing_features = np.setdiff1d(features, self.get_feature_list())
        return len(missing_features) == 0

    def get_feature_list(self, hemi="lh"):
        """Outputs a list of the features a participant has for each hemisphere"""
        with self.cohort._site_hdf5(self.site_code, self.group) as f:
            surf_dir_path = os.path.join(self.site_code, f[self.site_code].visit(self.find_path), hemi)
            keys =  list(f[surf_dir_path].keys())
            if ".on_lh.lesion.mgh" in keys:
                keys.remove(".on_lh.lesion.mgh")
        return keys

    def get_demographic_features(
        self, feature_names, csv_file=DEMOGRAPHIC_FEATURES_FILE, normalize=False, default=None
    ):
        """
        Read demographic features from csv file. Features are given as (partial) column titles

        Args:
            feature_names: list of partial column titles of features that should be returned
            csv_path: csv file containing demographics information.
                can be raw participants file or qc-ed values.
                "{site_code}" is replaced with current site_code.
            normalize: implemented for "Age of Onset" and "Duration"
            default: default value to be used when subject does not exist.
                Either "random" (which will choose a random value from the current
                demographics feature column) or any other value which will be used
                as default value.
        Returns:
            list of features, matching structure of feature_names
        """
        csv_path = csv_file
        return_single = False
        if isinstance(feature_names, str):
            return_single = True
            feature_names = [feature_names]
        df = pd.read_csv(csv_path, header=0, encoding="latin")
        # get index column
        id_col = None
        for col in df.keys():
            if "ID" in col:
                id_col = col
        # ensure that found an index column
        if id_col is None:
            self.log.warning("No ID column found in file, please check the csv file")

            return None
        df = df.set_index(id_col)
        # find desired demographic features
        features = []
        for desired_name in feature_names:
            matched_name = None
            for col in df.keys():
                if desired_name in col:
                    if matched_name is not None:
                        # already found another matching col
                        self.log.warning(
                            f"Multiple columns matching {desired_name} found ({matched_name}, {col}), please make search more specific"
                        )
                        return None
                    matched_name = col
            # ensure that found necessary data
            if matched_name is None:
                
                if "urfer" in desired_name:
                    matched_name = 'Freesurfer_nul'
                elif "Scanner" in desired_name:
                     return None
                else:
                    self.log.warning(f"Unable to find column matching {desired_name}, please double check for typos")
                    return None

            # read feature
            # if subject does not exists, add None
            if self.subject_id in df.index:
                if matched_name == 'Freesurfer_nul':
                    feature = '5.3'
                else:
                    feature = df.loc[self.subject_id][matched_name]
                if normalize:
                    if matched_name == "Age of onset":
                        feature = np.log(feature + 1)
                        feature = feature / df[matched_name].max()
                    elif matched_name == "Duration":
                        feature = (feature - df[matched_name].min()) / (df[matched_name].max() - df[matched_name].min())
                    else:
                        self.log.info(f"demographic feature normalisation not implemented for feature {matched_name}")
            elif default == "random":
                # unseeded rng for generating random numbers
                rng = np.random.default_rng()
                feature = np.clip(np.random.normal(0, 0.1) + rng.choice(df[matched_name]), 0, 1)
            else:
                feature = default
            features.append(feature)
        if return_single:
            return features[0]
        return features

    def load_feature_values(self, feature, hemi="lh"):
        """
        Load and return values of specified feature.
        """
        if 'label-dentate' in feature:
            NVERT=NVERT_DG
        elif 'label-avg' in feature:
            NVERT=NVERT_AVG
        else:
            NVERT=NVERT_HIPP
        feature_values = np.zeros(NVERT, dtype=np.float32)
        # read data from hdf5
        with self.cohort._site_hdf5(self.site_code, self.group) as f:
            surf_dir = f[os.path.join(self.site_code, f[self.site_code].visit(self.find_path), hemi)]
            if feature in surf_dir.keys():
                feature_values[:] = surf_dir[feature][:]
            else:
                self.log.debug(f"missing feature: {feature} set to zero")
        return feature_values

    def combine_DG_hippo(self, feature_base, hemi="lh"):
        vals_DG = self.load_feature_values(feature_base.format('dentate'), hemi)
        vals_hippo = self.load_feature_values(feature_base.format('hipp'), hemi)
        if (vals_DG.sum()!=0) & (vals_hippo.sum()!=0):
            return np.hstack([vals_DG[self.cohort.dentate_mask],vals_hippo[self.cohort.hippo_mask]])
        elif (vals_DG.sum()==0) & (vals_hippo.sum()!=0):
            return vals_hippo[self.cohort.hippo_mask]
        else:
            return np.zeros(1)

    def load_feature_lesion_data(self, features, hemi="lh", features_to_ignore=[]):
        """
        Load all patient's data into memory

        Args:
            features: list of features to be loaded
            hemi: 'lh' or 'rh'
            features_to_ignore: list of features that should be replaced with 0 upon loading

        Returns:
            feature_data, label

            TODO: check if loading multiple features at once is faster
        """
        # load all features
        feature_values = []
        for feature in features:
            if 'label-dentate' in feature:
                NVERT=NVERT_DG
            elif 'label-avg' in feature:
                NVERT=NVERT_AVG
            else:
                NVERT=NVERT_HIPP
            if feature in features_to_ignore:
                # append zeros for features_to_ignore
                feature_values.append(np.zeros(NVERT, dtype=np.float32))
            else:
                # read feature_values
                feature_values.append(self.load_feature_values(feature, hemi=hemi))
        feature_values = np.stack(feature_values, axis=-1)
        # load lesion data
        lesion_values = np.ceil(self.load_feature_values(".on_lh.lesion.mgh", hemi=hemi)).astype(int)

        return feature_values, lesion_values


    # TODO needed? -> asked
    def get_histology(self):
        """
        get histological classification from cleaned up demographics files
        """
        histology = self.get_demographic_features("Histo")
        return histology

    # TODO can be used to save new subjects
    # TODO write test
    def write_feature_values(self, feature, feature_values, hemis=["lh", "rh"], hdf5_file=None, hdf5_file_root=None):
        """
        write feature to subject's hdf5.

        Args:
            feature: name of the feature
            feature_values: feature values to be written to the hdf5
            hemis: hemispheres that should be written. If only one hemisphere is given,
            it is assumed that all values given with feature_values belong to this hemisphere.
            hdf5_file: uses self.cohort._site_hdf5 by default, but another filename can be specified,
                e.g. to write predicted lesions to another hdf5
            hdf5_file_root: optional to specify a different root from baseline, if writing to a new file
        """
        if 'label-dentate' in feature:
            NVERT=NVERT_DG
            mask = self.cohort.dentate_mask
        elif 'label-avg' in feature:
            NVERT=NVERT_AVG
            mask = self.cohort.avg_mask
        else:
            NVERT=NVERT_HIPP
            mask = self.cohort.hippo_mask
        # check that feature_values have expected length
        if hdf5_file_root is None:
            hdf5_file_root = self.cohort.hdf5_file_root
        assert len(feature_values) == sum(mask) * len(hemis)
        n_vert_cortex = sum(mask)
        # open hdf5 file
        if hdf5_file is not None:
            if not os.path.isfile(hdf5_file):
                hdf5_file_context = h5py.File(hdf5_file, "a")
            else:
                hdf5_file_context = h5py.File(hdf5_file, "r+")
        else:
            hdf5_file_context = self.cohort._site_hdf5(
                self.site_code, self.group, write=True, hdf5_file_root=hdf5_file_root
            )
        with hdf5_file_context as f:

            for i, hemi in enumerate(hemis):
                group = f.require_group(self.surf_dir_path(hemi))
                hemi_data = np.zeros(NVERT)
                hemi_data[mask] = feature_values[i * n_vert_cortex : (i + 1) * n_vert_cortex]
                dset = group.require_dataset(
                    feature, shape=(NVERT,), dtype="float32", compression="gzip", compression_opts=9
                )
                dset[:] = hemi_data

    def get_lesion_area(self):
        """
        calculate lesion area as the proportion of the hemisphere that is lesion.

        Returns:
            lesion_area, lesion_hemisphere, lesion_lobe
        """
        hemi = self.get_lesion_hemisphere()
        lobes_i, _, lobes_labels = self.cohort.lobes
        if hemi is not None:
            lesion = self.load_feature_values(".on_lh.lesion.mgh", hemi=hemi).astype(bool)
            total_area = np.sum(self.cohort.surf_area[self.cohort.hippo_mask])
            lesion_area = np.sum(self.cohort.surf_area[lesion]) / total_area
            locations = np.unique(lobes_i[lesion], return_counts=True)
            lobe = lobes_labels[locations[0][np.argmax(locations[1])]].decode()
            # set cingulate and insula to second most prevelant
            if lobe in ["cingulate", "insula"]:
                try:
                    lobe = lobes_labels[locations[0][np.argsort(locations[1])[-2]]].decode()
                except IndexError:
                    # one fail case was cingulate next to frontal, so frontal
                    lobe = "frontal"
        else:
            lesion_area = float("NaN")
            hemi = "NaN"
            lobe = "NaN"
        return lesion_area, hemi, lobe
