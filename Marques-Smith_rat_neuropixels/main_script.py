import matplotlib.pyplot as plt
import spikeextractors as se
import spiketoolkit as st
import spikewidgets as sw
import numpy as np
import scipy


p = './'
results_folder = p + 'results/'

bin_file = p + 'c1/c1_npx_raw.bin'
numchan = 384
dtype = 'int16'
samplerate = 30000
gain = 2.34

# load channel locations
chanMap = scipy.io.loadmat(p + 'chanMap.mat')
geom = np.squeeze(np.array([chanMap['xcoords'], chanMap['ycoords']])).T

recording = se.BinDatRecordingExtractor(datfile=bin_file, samplerate=samplerate,
                                        numchan=numchan, dtype=dtype, geom=geom,
                                        gain=gain)
recording_filt = st.preprocessing.bandpass_filter(recording)

# dump filtered data
se.write_binary_dat_format(recording=recording_filt, save_path=results_folder + 'rec_filt.dat',
                           dtype='float32', chunksize=20)

recording_filt = se.BinDatRecordingExtractor(datfile=results_folder + 'rec_filt.dat', samplerate=samplerate,
                                             numchan=numchan, dtype='float32', geom=geom)

recording_cmr = st.preprocessing.common_reference(recording_filt, reference='median')

rec_dict = {'rec': recording_cmr}


sorter_list = ['herdingspikes', 'ironclust', 'kilosort2',
               'mountainsort4', 'spykingcircus', 'tridesclous']

sorter_params = {'mountainsort4': {'adjacency_radius': 50},
                 'spyking_circus': {'adjacency_radius': 50}}

result_dict = st.sorters.run_sorters(sorter_list=sorter_list, recording_dict_or_list=rec_dict, with_output=True,
                                     debug=True, sorter_params=sorter_params)

print('-----------------------------------------')
print('Saving results')
for s in sorter_list:
    sorting = result_dict['rec'][s]
    se.NpzSortingExtractor.write_sorting(sorting, results_folder + s + '.npz')
