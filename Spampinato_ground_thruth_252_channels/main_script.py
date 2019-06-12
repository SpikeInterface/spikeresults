# -*- coding: utf-8 -*-
import zipfile, tarfile
import re
import os, shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import spiketoolkit as st
import spikeextractors as se
from spiketoolkit.comparison import (setup_comparison_study, run_study_sorters,
            aggregate_sorting_comparison, aggregate_performances_table)

# my working path
# basedir = '/media/samuel/SamCNRS/DataSpikeSorting/pierre/zenodo/'
# basedir = '/media/samuel/dataspikesorting/DataSpikeSortingHD2/Pierre/zenodo/'
#~ basedir = '/mnt/data/sam/DataSpikeSorting/pierre_zenodo/'
basedir = '/home/samuel/DataSpikeSorting/Pierre/zenodo/'

# input file
recording_folder = basedir + 'original_files/'

# where output will be
study_folder = basedir + 'study_gt254/'


# ground truth information
ground_truth_folder = basedir + 'ground_truth/'

# file_list

#~ all_rec_names = ['20170629_patch3', '20170728_patch2', '20170630_patch1', '20160426_patch2', '20170621_patch1',
             #~ '20170627_patch1', '20170706_patch3', '20170706_patch1', '20170726_patch1', '20170725_patch1',
             #~ '20160426_patch3', '20170622_patch1', '20170623_patch1', '20170622_patch2', '20170629_patch2',
             #~ '20170713_patch1', '20160415_patch2', '20170706_patch2', '20170803_patch1']

rec_names = [ '20160415_patch2', '20170803_patch1', '20170623_patch1', '20170622_patch1', '20160426_patch3', 
            '20170725_patch1', '20170621_patch1', '20160426_patch2', '20170728_patch2']


#~ rec_names = [ '20160415_patch2', '20170803_patch1',]
# rec_names = [ '20160415_patch2', ]



#~ bad = ['20170706_patch2', # noisy
        #~ '20170713_patch1', # double peak
        #~ '20170629_patch2', # near thresh
        #~ '20170622_patch2', # too small
        #~ '20170726_patch1', # near thresh
        #~ '20170706_patch1', # near thresh
        #~ '20170706_patch3', # near thresh
        #~ '20170627_patch1', #near thresh
        #~ '20170630_patch1', # double peak
        #~ '20170629_patch3', #near thresh
        #~ ]
        
        
        
        
        



# sorter list
# sorter_list = ['tridesclous', 'mountainsort4', ]
sorter_list = ['tridesclous']




def setup_study():
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

        gt_dict[rec_name] = (rec, sorting_gt)
    
    setup_comparison_study(study_folder, gt_dict)
        

def run_all():
    #~ sorter_list = ['tridesclous', 'herdingspikes', ]   # 'mountainsort4' 
    #~ sorter_list = ['klusta', ]
    sorter_list = ['tridesclous', ]
    run_study_sorters(study_folder, sorter_list, mode='keep', engine='loop')
    



def collect_results():
    comparisons = aggregate_sorting_comparison(study_folder, exhaustive_gt=True)
    dataframes = aggregate_performances_table(study_folder, exhaustive_gt=True)
    
    #~ for (rec_name, sorter_name), comp in comparisons.items():
        #~ comp = comparisons[('001_synth', 'tridesclous')]
        #~ print()
        #~ print(rec_name, sorter_name)
        #~ print(comp.count)
        #~ comp.print_summary()
    
    #~ plt.subplots()
        #~ comp.plot_confusion_matrix()
    
    dataframes['raw_counts']
    
    plt.show()



if __name__ == '__main__':
    #~ unzip_all()
    #~ setup_study()
    run_all()
    
    
    #~ collect_results()
    
    
    

