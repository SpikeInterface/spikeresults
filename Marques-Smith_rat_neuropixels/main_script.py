import matplotlib.pyplot as plt
import spikeextractors as se
import spiketoolkit as st
import pandas as pd
import spikewidgets as sw
import numpy as np
import scipy
import seaborn as sns
from pathlib import Path
import os

p = Path('.')
results_folder = p / 'results'
working_folder = p / 'working'

if not os.path.isdir(results_folder):
    os.mkdir(results_folder)

bin_file = p / 'c1' / 'c1_npx_raw.bin'
numchan = 384
dtype = 'int16'
samplerate = 30000
gain = 2.34

# load channel locations
chanMap = scipy.io.loadmat(p / 'chanMap.mat')
geom = np.squeeze(np.array([chanMap['xcoords'], chanMap['ycoords']])).T

if not (working_folder / 'rec_filt.dat').is_file():
    print('-----------------------------------------')
    print('Preprocessing recording')
    recording = se.BinDatRecordingExtractor(datfile=bin_file, samplerate=samplerate,
                                            numchan=numchan, dtype=dtype, geom=geom,
                                            gain=gain)
    recording_filt = st.preprocessing.bandpass_filter(recording)

    # dump filtered data
    se.write_binary_dat_format(recording=recording_filt, save_path=working_folder / 'rec_filt.dat',
                               dtype='float32', chunksize=20)

recording_filt = se.BinDatRecordingExtractor(datfile=working_folder / 'rec_filt.dat', samplerate=samplerate,
                                             numchan=numchan, dtype='float32', geom=geom)

recording_cmr = st.preprocessing.common_reference(recording_filt, reference='median')

rec_dict = {'rec': recording_cmr}
sorter_list = ['tridesclous', 'spykingcircus', 'mountainsort4', 'kilosort2', 'herdingspikes', 'ironclust']
sorter_params = {'mountainsort4': {'adjacency_radius': 50},
                 'spyking_circus': {'adjacency_radius': 50}}


if not (results_folder / 'sortings').is_dir():
    print('-----------------------------------------')
    print('Running sorters')
    result_dict = st.sorters.run_sorters(sorter_list=sorter_list, recording_dict_or_list=rec_dict, with_output=True,
                                         debug=True, sorter_params=sorter_params, working_folder=working_folder)

    print('-----------------------------------------')
    print('Saving results')
    for s in sorter_list:
        sorting = result_dict[('rec', s)]
        se.NpzSortingExtractor.write_sorting(sorting, results_folder / 'sortings' / str(s + '.npz'))

print('-----------------------------------------')
print('Loading sorting output')

exclude_sorters = ['mountainsort4',  'tridesclous']
sorting_dict = {}
sortings = []
sortings_names = []
for s in (results_folder / 'sortings').iterdir():
    if s.suffix == '.npz':
        if s.stem not in exclude_sorters:
            sort = se.NpzSortingExtractor(s)
            sorting_dict[s.stem] = sort
            sortings.append(sort)
            sortings_names.append(s.stem)


mcmp = st.comparison.compare_multiple_sorters(sorting_list=sortings, name_list=sortings_names, verbose=True)
w = sw.plot_multicomp_graph(mcmp, draw_labels=False, colorbar=True, alpha_edges=0.2, node_cmap='rainbow')

n_units = []
sorters = []
for (sname, s) in sorting_dict.items():
    n_units.append(len(s.get_unit_ids()))
    sorters.append(sname)
    print(sname, len(s.get_unit_ids()))

agreement_sortings = {}
for i in range(1, len(sortings_names)):
    sort_agreement = mcmp.get_agreement_sorting(minimum_matching=i+1)
    agreement_sortings[i+1] = sort_agreement
    n_units.append(len(sort_agreement.get_unit_ids()))
    sorters.append('agr.'+str(i+1))
    print('agr.', i+1, len(sort_agreement.get_unit_ids()))

data = {'sorters': sorters, 'n_units': n_units}
df = pd.DataFrame(data=data)

ax = sns.barplot(x='sorters', y='n_units', data=df, orient=45)
ax.set_xlabel('')
ax.set_ylabel('Number of units', fontsize=20)
ax.yaxis.set_tick_params(labelsize=12)
ax.set_xticklabels(sorters, fontsize=15, rotation=45, ha='center')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

groupedvalues = df.reset_index()

for index, row in groupedvalues.iterrows():
    ax.text(row.name, row.n_units + 2, int(row.n_units), color='black', ha="center")

figsns = ax.get_figure()
figsns.subplots_adjust(bottom=0.2)
