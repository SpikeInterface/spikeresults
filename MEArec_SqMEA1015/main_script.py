import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import spikeextractors as se
from spiketoolkit.study import GroundTruthStudy
import spikewidgets as sw
from pathlib import Path

plot_mearec = False

def clean_plot(ax, label, sorters):
    ax.set_xlabel('')
    ax.set_ylabel(label, fontsize=20)
    ax.yaxis.set_tick_params(labelsize=12)
    ax.set_xticklabels(sorters, fontsize=15, rotation=45, ha='center')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig = ax.get_figure()
    fig.subplots_adjust(bottom=0.2)
    fig.set_size_inches(8, 7)

p = Path('.')

study_folder = p / 'study_mearec_SqMEA1015um'

mearec_filename = p / 'recordings_50cells_SqMEA-10-15um_60.0_10.0uV_27-03-2019_13-31.h5'
rec0 = se.MEArecRecordingExtractor(mearec_filename)
gt_sorting0 = se.MEArecSortingExtractor(mearec_filename)
study = None

if plot_mearec:
    import MEArec as mr
    import MEAutility as mu

    recgen = mr.load_recordings(mearec_filename)

    # plot the probe
    probe_info = recgen.info['electrodes']
    probe_name = recgen.info['electrodes']['electrode_name']
    mea = mu.return_mea(info=probe_info)
    fig1, ax1 = plt.subplots()
    mu.plot_probe(mea, ax=ax1)
    ax1.axis('off')

    fig2, axs = plt.subplots(nrows=3, ncols=4)
    for i, unit_id in enumerate(gt_sorting0.get_unit_ids()[:12]):
        ax = axs.flatten()[i]
        mr.plot_templates(recgen, template_ids=unit_id, ax=ax)
        ax.set_title('unit #{}'.format(unit_id))

    fig3, ax3 = plt.subplots()
    mr.plot_recordings(recgen, start_time=0, end_time=5, lw=0.1, ax=ax3)

# Setup study folder
if not study_folder.is_dir():
    print('Setting up study folder:', study_folder)
    gt_dict = {'rec0': (rec0, gt_sorting0)}
    study = GroundTruthStudy.create(study_folder, gt_dict)

if study is None:
    study = GroundTruthStudy(study_folder)

# Run sorters
sorter_list = ['herdingspikes', 'kilosort2', 'ironclust',
               'spykingcircus', 'tridesclous']
sorter_params = {'mountainsort4': {'adjacency_radius': 50},
                 'spykingcircus': {'adjacency_radius': 50}}

if not (study_folder / 'sorter_folders').is_dir():
    print('Running sorters')
    study.run_sorters(sorter_list, mode='keep', engine='loop')

# Perform comparisons
print('Performing comparisons and getting results')
study.run_comparisons(exhaustive_gt=True, compute_misclassification=True)

comparisons = study.comparisons
dataframes = study.aggregate_dataframes(accuracy=0.8)

# Plot confusion matrices
fig4 = plt.figure()
for i, ((rec_name, sorter_name), comp) in enumerate(comparisons.items()):
    print(rec_name, sorter_name)
    comp.print_summary(accuracy=0.8)

    ax = fig4.add_subplot(2, 3, i + 1)
    sw.plot_confusion_matrix(comp, ax=ax, count_text=False, unit_ticks=False)
    ax.set_title(sorter_name)

plt.show()

run_times = dataframes['run_times']
perf_units = dataframes['perf_by_units']
perf_avg = dataframes['perf_pooled_with_average']
count_units = dataframes['count_units']

exclude_sorters = ['mountainsort4',  'tridesclous']

if len(exclude_sorters) > 0:
    for name in exclude_sorters:
        run_times = run_times[run_times['sorter_name'] != name]
        perf_units = perf_units[perf_units['sorter_name'] != name]
        perf_avg = perf_avg[perf_avg['sorter_name'] != name]
        count_units = count_units[count_units['sorter_name'] != name]

sorters = run_times['sorter_name']

fig5, ax5 = plt.subplots()
ax5 = sns.barplot(data=dataframes['run_times'], x='sorter_name', y='run_time', ax=ax5, order=sorters)
fig6, ax6 = plt.subplots()
ax6 = sns.swarmplot(data=dataframes['perf_by_units'], x='sorter_name', y='accuracy', ax=ax6, order=sorters)
fig7, ax7 = plt.subplots()
ax7 = sns.barplot(data=dataframes['perf_pooled_with_average'], x='sorter_name', y='precision', ax=ax7, order=sorters)
fig8, ax8 = plt.subplots()
ax8 = sns.barplot(data=dataframes['count_units'], x='sorter_name', y='num_bad', ax=ax8, order=sorters)

sorters = run_times['sorter_name']

clean_plot(ax5, 'run times (s)', sorters)
clean_plot(ax6, 'accuracy', sorters)
clean_plot(ax7, 'precision', sorters)
clean_plot(ax8, 'bad units', sorters)
