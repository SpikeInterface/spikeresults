import os
import time

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn

import spiketoolkit as st
import spikeextractors as se
from spiketoolkit.comparison import (setup_comparison_study, run_study_sorters,
            aggregate_sorting_comparison, aggregate_performances_table)


os.environ["IRONCLUST_PATH"] = '/home/samuel/smb4k/CRNLDATA/home/samuel.garcia/Documents/ironclust/'
os.environ["KILOSORT_PATH"] = '/home/samuel/smb4k/CRNLDATA/home/samuel.garcia/Documents/KiloSort/'
os.environ["NPY_MATLAB_PATH"] = '/home/samuel/smb4k/CRNLDATA/home/samuel.garcia/Documents/npy-matlab/'
os.environ["KILOSORT2_PATH"] = '/home/samuel/smb4k/CRNLDATA/home/samuel.garcia/Documents/Kilosort2/'



#~ p = '/media/samuel/SamCNRS/DataSpikeSorting/mearec/'
p = '/media/samuel/dataspikesorting/DataSpikeSortingHD2/mearec/'
#~ p = '/home/samuel/DataSpikeSorting/mearec/'


study_folder = p + 'study_mearec'


def setup():
    
    mearec_filename = p + 'recordings_50cells_SqMEA-10-15um_60.0_10.0uV_27-03-2019_13_31.h5'

    rec0  = se.MEArecRecordingExtractor(mearec_filename, locs_2d=False)
    gt_sorting0 = se.MEArecSortingExtractor(mearec_filename)
    for chan in rec0.get_channel_ids():
        loc = rec0.get_channel_property(chan, 'location')
        rec0.set_channel_property(chan, 'location', loc[1:])
    
    gt_dict = {'rec0' : (rec0, gt_sorting0) }
    
    setup_comparison_study(study_folder, gt_dict)
    
    
    
def run():
    #~ sorter_list = ['tridesclous', 'herdingspikes', 'klusta', 'spykingcircus']   # 'mountainsort4'  'ironclust', 'kilosort', 'kilosort2', 'spykingcircus'
    sorter_list = ['tridesclous' ]
    
    run_study_sorters(study_folder, sorter_list, mode='keep', engine='loop')

def collect_results():
    comparisons = aggregate_sorting_comparison(study_folder, exhaustive_gt=True)
    dataframes = aggregate_performances_table(study_folder, exhaustive_gt=True)
    
    for (rec_name, sorter_name), comp in comparisons.items():
        #~ comp = comparisons[('001_synth', 'tridesclous')]
        print()
        print(rec_name, sorter_name)
        print(comp.count)
        comp.print_summary()
    
    #~ plt.subplots()
        fig, ax = plt.subplots()
        comp.plot_confusion_matrix(ax=ax)
        fig.suptitle(rec_name + '  ' + sorter_name)
    
    
    
    #~ dataframes['perf_by_spiketrain']
    
    plt.show()

    
if __name__ == '__main__':
    #~ setup()
    #~ run()
    
    collect_results()


