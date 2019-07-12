import os


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import spikeextractors as se
from spiketoolkit.study import GroundTruthStudy
import spikewidgets as sw


p = './'


study_folder = p + 'study_mearec_SqMEA1015um'

mearec_filename = p + 'recordings_50cells_SqMEA-10-15um_60.0_10.0uV_27-03-2019_13-31.h5'
rec0  = se.MEArecRecordingExtractor(mearec_filename)
gt_sorting0 = se.MEArecSortingExtractor(mearec_filename)

# Setup study folder
if not os.path.isdir(study_folder):
    print('Setting up study folder:', study_folder)
    gt_dict = {'rec0': (rec0, gt_sorting0)}
    GroundTruthStudy.setup(study_folder, gt_dict)

# Run sorters
print('Running sorters')
sorter_list = ['mountainsort4', 'spykingcircus', 'tridesclous']
sorter_params = {'mountainsort4': {'adjacency_radius': 50}, 
		 'spykingcircus': {'adjacency_radius': 50}}
study = GroundTruthStudy(study_folder)

if not os.path.isdir(study_folder + '/sorter_folders'):
    study.run_sorters(sorter_list, mode='keep', engine='loop')


# Perform comparisons
print('Performing comparisons and getting results')
study.run_comparisons(exhaustive_gt=True)

comparisons = study.comparisons
dataframes = study.aggregate_dataframes(accuracy=0.9)

# Plot confusion matrices
fig1 = plt.figure()
for i, ((rec_name, sorter_name), comp) in enumerate(comparisons.items()):
    print(rec_name, sorter_name)
    comp.print_summary()

    ax = fig1.add_subplot(2, 3, i+1)
    sw.plot_confusion_matrix(comp, ax=ax, count_text=False, unit_ticks=False)
    ax.set_title(sorter_name)

plt.show()

count_units = dataframes['count_units']
perf_units = dataframes['perf_by_units']
run_times = dataframes['run_times']


fig2, ax = plt.subplots(2, 4)
sns.barplot(data=run_times, x='sorter_name', y='run_time', ax=ax[0, 0])

sns.swarmplot(data=perf_units, x='sorter_name', y='accuracy', ax=ax[0, 1])
ax[0, 1].axhline(0.8, ls='--', color='red')

sns.swarmplot(data=perf_units, x='sorter_name', y='precision', ax=ax[0, 2])

sns.swarmplot(data=perf_units, x='sorter_name', y='recall', ax=ax[0, 3])


sns.barplot(data=count_units, x='sorter_name', y='num_well_detected', ax=ax[1, 0])
ax[1, 0].axhline(50, ls='--', color='red')

sns.barplot(data=count_units, x='sorter_name', y='num_false_positive', ax=ax[1, 1])
ax[1, 1].axhline(50, ls='--', color='red')

sns.barplot(data=count_units, x='sorter_name', y='num_redundant', ax=ax[1, 2])
ax[1, 2].axhline(50, ls='--', color='red')

sns.barplot(data=count_units, x='sorter_name', y='num_redundant', ax=ax[1, 3])
ax[1, 3].axhline(50, ls='--', color='red')
