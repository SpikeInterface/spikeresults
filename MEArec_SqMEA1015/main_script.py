import os


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import spikeextractors as se
from spiketoolkit.study import GroundTruthStudy
import spikewidgets as sw


p = './'


study_folder = p + 'study_mearec_SqMEA1015um'

# Setup study folder
# print('Setting up study folder:', study_folder)
mearec_filename = p + 'recordings_50cells_SqMEA-10-15um_60.0_10.0uV_27-03-2019_13-31.h5'
rec0  = se.MEArecRecordingExtractor(mearec_filename)
gt_sorting0 = se.MEArecSortingExtractor(mearec_filename)
# gt_dict = {'rec0': (rec0, gt_sorting0)}
# GroundTruthStudy.setup(study_folder, gt_dict)

# Run sorters
print('Running sorters')
sorter_list = ['herdingspikes', 'ironclust', 'kilosort2',
               'mountainsort4', 'spykingcircus', 'tridesclous']
study = GroundTruthStudy(study_folder)
study.run_sorters(sorter_list, mode='keep', engine='loop')


# Perform comparisons
print('Performing comparisons and getting results')
study.run_comparisons(exhaustive_gt=False)

comparisons = study.comparisons
dataframes = study.aggregate_dataframes()

# # Plot confusion matrices
# fig = plt.figure()
# for i, ((rec_name, sorter_name), comp) in enumerate(comparisons.items()):
#     print(rec_name, sorter_name)
#     comp.print_summary()
#
#     ax = fig.add_subplot(2, 2, i+1)
#     sw.plot_confusion_matrix(comp, ax=ax, count_text=False)
#     fig.suptitle(rec_name + '  ' + sorter_name)
#
# plt.show()
    
    


