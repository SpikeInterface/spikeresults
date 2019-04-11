# -*- coding: utf-8 -*-


import zipfile, tarfile
import re
import os, shutil

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import spiketoolkit as st
import spikeextractors as se 
import spikewidgets as sw

# this tridesclous utils are imported only for juxta detection to keep this script simple
from tridesclous.peakdetector import  detect_peaks_in_chunk
from tridesclous.tools import median_mad
from tridesclous.waveformtools import extract_chunks


# my working path
# basedir = '/media/samuel/SamCNRS/DataSpikeSorting/pierre/zenodo/'
# basedir = '/media/samuel/dataspikesorting/DataSpikeSortingHD2/Pierre/zenodo/'
basedir = '/mnt/data/sam/DataSpikeSorting/pierre_zenodo/'

# input file
recording_folder = basedir + 'rawfiles/'

# where output will be
working_folder = basedir + 'run_comparison/'

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


def unzip_all():
    for rec_name in rec_names:
        filename = recording_folder + rec_name + '.tar.gz'

        if os.path.exists(recording_folder+rec_name) and os.path.isdir(recording_folder+rec_name):
            continue
        t = tarfile.open(filename, mode='r|gz')
        t.extractall(recording_folder+rec_name)


def run_all():
    recordings = {}
    for rec_name in rec_names:
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

        recordings[rec_name] = rec
        
    results = st.sorters.run_sorters(sorter_list, recordings, working_folder, grouping_property='group',
                                                        debug=False, shared_binary_copy=True)



def benchmark_results():
    ground_truths = {}
    for rec_name in rec_names:
        gt_indexes = np.fromfile(ground_truth_folder + rec_name + '/juxta_peak_indexes.raw', dtype='int64')
        gt_sorting = se.NumpySortingExtractor()
        gt_sorting.setTimesLabels(gt_indexes, np.zeros(gt_indexes.size, dtype='int64'))
        ground_truths[rec_name] = gt_sorting

    # compute performance
    comparisons, comp_dataframes = st.comparison.gather_sorting_comparison(working_folder, ground_truths,use_multi_index=True)
    print(comp_dataframes)
    
    for (rec_name, sorter_name), comp in comparisons.items():
        print()
        print(rec_name, sorter_name)
        print(ground_truths[rec_name].get_unit_spike_train(0).size)
        
        comp._do_confusion()
        
        ax = comp.plot_confusion_matrix()
        plt.show()
        
        print(comp._confusion_matrix[:, :1], comp._confusion_matrix[:, -1:])
        #~ ax.set_title('{} {}'.format(rec_name, sorter_name))
        
    
    
    

if __name__ == '__main__':
    # unzip_all()
    #~ run_all()
    # detect_ground_truth_spike_on_juxta()
    benchmark_results()
    

    
    

