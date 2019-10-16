import spikeinterface.extractors as se
import spikeinterface.comparison as GroundTruthStudy
from pathlib import Path

p = Path('.')

study_folder = p / 'study_mearec_SqMEA1015um'

mearec_filename = p / 'recordings_50cells_SqMEA-10-15um_60.0_10.0uV_27-03-2019_13-31.h5'
rec0 = se.MEArecRecordingExtractor(mearec_filename)
gt_sorting0 = se.MEArecSortingExtractor(mearec_filename)
study = None

# Setup study folder
if not study_folder.is_dir():
    print('Setting up study folder:', study_folder)
    gt_dict = {'rec0': (rec0, gt_sorting0)}
    study = GroundTruthStudy.create(study_folder, gt_dict)

if study is None:
    study = GroundTruthStudy(study_folder)

# Run sorters
sorter_list = ['herdingspikes', 'kilosort2', 'ironclust',
               'spykingcircus', 'tridesclous', 'mountainsort4']
sorter_params = {'mountainsort4': {'adjacency_radius': 50},
                 'spykingcircus': {'adjacency_radius': 50}}

if not (study_folder / 'sorter_folders').is_dir():
    print('Running sorters')
    study.run_sorters(sorter_list, mode='keep', engine='loop')
