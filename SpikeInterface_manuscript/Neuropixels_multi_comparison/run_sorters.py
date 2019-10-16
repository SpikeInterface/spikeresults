import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import numpy as np
import scipy
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
sampling_frequency = 30000
gain = 2.34

# load channel locations
chanMap = scipy.io.loadmat(p / 'chanMap.mat')
geom = np.squeeze(np.array([chanMap['xcoords'], chanMap['ycoords']])).T

if not (working_folder / 'rec_filt.dat').is_file():
    print('-----------------------------------------')
    print('Preprocessing recording')
    recording = se.BinDatRecordingExtractor(file_path=bin_file, sampling_frequency=sampling_frequency,
                                            numchan=numchan, dtype=dtype, geom=geom,
                                            gain=gain)
    recording_filt = st.preprocessing.bandpass_filter(recording)

    # dump filtered data
    se.write_binary_dat_format(recording=recording_filt, save_path=working_folder / 'rec_filt.dat',
                               dtype='float32', chunk_size=20)

recording_filt = se.BinDatRecordingExtractor(file_path=working_folder / 'rec_filt.dat',
                                             sampling_frequency=sampling_frequency,
                                             numchan=numchan, dtype='float32', geom=geom)

recording_cmr = st.preprocessing.common_reference(recording_filt, reference='median')

rec_dict = {'rec': recording_cmr}
sorter_list = ['tridesclous', 'spykingcircus', 'mountainsort4', 'kilosort2', 'herdingspikes', 'ironclust']
sorter_params = {'mountainsort4': {'adjacency_radius': 50},
                 'spyking_circus': {'adjacency_radius': 50}}

if not (results_folder / 'sortings').is_dir():
    print('-----------------------------------------')
    print('Running sorters')
    result_dict = ss.run_sorters(sorter_list=sorter_list, recording_dict_or_list=rec_dict, with_output=True,
                                 debug=True, sorter_params=sorter_params, working_folder=working_folder)

    print('-----------------------------------------')
    print('Saving results')
    for s in sorter_list:
        sorting = result_dict[('rec', s)]
        se.NpzSortingExtractor.write_sorting(sorting, results_folder / 'sortings' / str(s + '.npz'))

print('-----------------------------------------')
print('Loading sorting output')

exclude_sorters = []
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
