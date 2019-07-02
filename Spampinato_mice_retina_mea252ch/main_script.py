# -*- coding: utf-8 -*-
import zipfile, tarfile
import re
import os, shutil
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import spiketoolkit as st
import spikeextractors as se

from spiketoolkit.study import GroundTruthStudy

#~ from spiketoolkit.comparison import (setup_comparison_study, run_study_sorters,
            #~ aggregate_sorting_comparison, aggregate_performances_table)
#~ from spiketoolkit.comparison.groundtruthstudy import copy_sorting



os.environ["IRONCLUST_PATH"] = '/home/samuel/smb4k/CRNLDATA/home/samuel.garcia/Documents/ironclust/'
os.environ["KILOSORT_PATH"] = '/home/samuel/smb4k/CRNLDATA/home/samuel.garcia/Documents/KiloSort/'
os.environ["NPY_MATLAB_PATH"] = '/home/samuel/smb4k/CRNLDATA/home/samuel.garcia/Documents/npy-matlab/'
os.environ["KILOSORT2_PATH"] = '/home/samuel/smb4k/CRNLDATA/home/samuel.garcia/Documents/Kilosort2/'

# my working path
basedir = '/media/samuel/SamCNRS/DataSpikeSorting/pierre/zenodo/'
#~ basedir = '/media/samuel/dataspikesorting/DataSpikeSortingHD2/Pierre/zenodo/'
#~ basedir = '/mnt/data/sam/DataSpikeSorting/pierre_zenodo/'
#~ basedir = '/home/samuel/DataSpikeSorting/Pierre/zenodo/'
#~ basedir = '/media/samuel/dataspikesorting/DataSpikeSortingHD2/Pierre/zenodo/'

# input file
recording_folder = basedir + 'original_files/'

# where output will be
study_folder = basedir + 'study_gt252/'


# ground truth information
ground_truth_folder = basedir + 'ground_truth/'



def setup_study():
    rec_names = [
        '20160415_patch2',
        '20160426_patch2', 
        '20160426_patch3', 
        '20170621_patch1',
        '20170713_patch1',
        '20170725_patch1',
        '20170728_patch2',
        '20170803_patch1',
    ]
    
    gt_dict = {}
    for rec_name in rec_names:
        
        # find raw file
        dirname = recording_folder + rec_name + '/'
        for f in os.listdir(dirname):
            if f.endswith('.raw') and not f.endswith('juxta.raw'):
                mea_filename = dirname + f

        # raw files have an internal offset that depend on the channel count
        # a simple built header can be parsed to get it
        with open(mea_filename.replace('.raw', '.txt'), mode='r') as f:
            offset = int(re.findall('padding = (\d+)', f.read())[0])
        
        # recording
        rec = se.BinDatRecordingExtractor(mea_filename, 20000., 256, 'uint16', offset=offset, frames_first=True)
        
        # this reduce channel count to 252
        rec = se.load_probe_file(rec, basedir + 'mea_256.prb')

        # gt sorting
        gt_indexes = np.fromfile(ground_truth_folder + rec_name + '/juxta_peak_indexes.raw', dtype='int64')
        sorting_gt = se.NumpySortingExtractor()
        sorting_gt.set_times_labels(gt_indexes, np.zeros(gt_indexes.size, dtype='int64'))
        sorting_gt.set_sampling_frequency(20000.0)

        gt_dict[rec_name] = (rec, sorting_gt)
    
    study = GroundTruthStudy.setup(study_folder, gt_dict)

def run_all():
    study = GroundTruthStudy(study_folder)
    sorter_list = ['tridesclous', 'herdingspikes', 'mountainsort4' ]
    #~ sorter_list = ['herdingspikes']
    study.run_sorters(sorter_list, mode='keep', engine='loop')


def collect_results():
    study = GroundTruthStudy(study_folder)
    #~ study.copy_sortings()
    
    print(study)
    
    study.run_comparisons(exhaustive_gt=False)
    
    comparisons = study.comparisons
    dataframes = study.aggregate_dataframes()
    
    
    for (rec_name, sorter_name), comp in comparisons.items():
        print()
        print(rec_name, sorter_name)
        print(comp.count)
        comp.print_summary()
        
    
    #~ plt.subplots()
        #~ comp.plot_confusion_matrix()
    
    print(dataframes.keys())
    print(dataframes['perf_pooled_with_average'])
    
        #~ plt.show()



if __name__ == '__main__':
    #~ setup_study()
    #~ run_all()
    
    
    collect_results()
    
    

    
    
    
    
    

