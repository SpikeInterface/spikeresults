# -*- coding: utf-8 -*-
"""
Helper script to prepare the dataset:
  * unzip evrything
  * run a juxta cellular detection
  * generate figure to check manual juxta cellular quality

"""
import matplotlib

import os, shutil
import zipfile, tarfile
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# this tridesclous utils are imported only for juxta detection to keep this script simple
from tridesclous.peakdetector import  detect_peaks_in_chunk
from tridesclous.tools import median_mad
from tridesclous.waveformtools import extract_chunks


# my working path (I have several machine)
basedir = '/media/samuel/SamCNRS/DataSpikeSorting/pierre/zenodo/'
# basedir = '/mnt/data/sam/DataSpikeSorting/pierre_zenodo/'
# basedir = '/home/samuel/DataSpikeSorting/Pierre/zenodo/'

# input file
recording_folder = basedir + 'original_files/'

# ground truth information
ground_truth_folder = basedir + 'ground_truth/'

# file_list
# rec_names = [ e for e in os.listdir(recording_folder) if os.path.isdir(recording_folder + e)]
rec_names = ['20170629_patch3', '20170728_patch2', '20170630_patch1', '20160426_patch2', '20170621_patch1',
             '20170627_patch1', '20170706_patch3', '20170706_patch1', '20170726_patch1', '20170725_patch1',
             '20160426_patch3', '20170622_patch1', '20170623_patch1', '20170622_patch2', '20170629_patch2',
             '20170713_patch1', '20160415_patch2', '20170706_patch2', '20170803_patch1']

rec_names = ['20170706_patch2']

def unzip_all():
    # this unzip all files into recording_folder
    for rec_name in rec_names:
        filename = recording_folder + rec_name + '.tar.gz'

        if os.path.exists(recording_folder+rec_name) and os.path.isdir(recording_folder+rec_name):
            continue
        t = tarfile.open(filename, mode='r|gz')
        t.extractall(recording_folder+rec_name)


def detect_ground_truth_spike_on_juxta():
    """
    The detect spike on the juxta cellular recording.
    Then it extract the waveforms from mea signals with that ground truth indexes.
    So
    """
    
    if not os.path.exists(ground_truth_folder):
        os.mkdir(ground_truth_folder)
    
    gt_info = pd.DataFrame(index=rec_names)
    
    for rec_name in rec_names:
        print('detect_juxta: ', rec_name)
        
        # get juxta signal
        dirname = recording_folder + rec_name + '/'
        for f in os.listdir(dirname):
            if  f.endswith('juxta.raw'):
                juxta_filename = dirname + f
        juxta_sig = np.memmap(juxta_filename, dtype='float32')
        
        # get mea signals
        for f in os.listdir(dirname):
            if f.endswith('.raw') and not f.endswith('juxta.raw'):
                mea_filename = dirname + f
        with open(mea_filename.replace('.raw', '.txt'), mode='r') as f:
            offset = int(re.findall('padding = (\d+)', f.read())[0])
        mea_sigs = np.memmap(mea_filename, dtype='uint16', offset=offset).reshape(-1, 256)
        
        # select only the 252 mea channel (see PRB file)
        mea_sigs = mea_sigs[:, list(range(126)) + list(range(128,254))]
        
        gt_folder = ground_truth_folder + rec_name + '/'
        os.mkdir(gt_folder)
        
        # detect spikes
        med, mad = median_mad(juxta_sig)
        thresh = med + 8*mad
        gt_indexes = detect_peaks_in_chunk(juxta_sig[:, None], k=10,thresh=thresh, peak_sign='-')
        gt_indexes = gt_indexes.astype('int64')
        gt_indexes.tofile(gt_folder+'juxta_peak_indexes.raw')
        
        # save some figures to for visual cheking
        sr = 20000.
        times = np.arange(juxta_sig.size) / sr

        fig, ax = plt.subplots()
        ax.plot(times, juxta_sig)
        ax.plot(times[gt_indexes], juxta_sig[gt_indexes], ls='None', color='r', marker='o')
        ax.set_xlim(0, 10)
        ax.axhline(-thresh, color='k', ls='--')
        ax.set_title('juxta detection - ' + rec_name)
        fig.savefig(gt_folder+'juxta detection.png')
        
        fig, ax = plt.subplots()
        count, bins = np.histogram(juxta_sig[gt_indexes], bins=np.arange(np.min(juxta_sig[gt_indexes]), 0,  0.5))
        ax.plot(bins[:-1], count)
        ax.axvline(-thresh, color='k', ls='--')
        ax.set_title('juxta peak amplitude - ' + rec_name)
        fig.savefig(gt_folder+'juxta peak amplitude.png')
        
        # extract waveforms with only 150 peaks to minimize RAM
        n_left, n_right = -45, 60
        some_gt_indexes = np.random.choice(gt_indexes, size=150)
        waveforms = extract_chunks(mea_sigs, some_gt_indexes+n_left, n_right-n_left)
        wf_median, wf_mad = median_mad(waveforms, axis=0)
        
        
        # get on wich channel the max is and the value
        max_on_channel = np.argmin(np.min(wf_median, axis=0), axis=0)

        # get the MAD (robust STD) on the mea signal
        # this estimate the SNR
        mea_median, mea_mad = median_mad(mea_sigs[:, max_on_channel] , axis=0)
        baseline = mea_median
        
        peak_value = np.min(wf_median[:, max_on_channel])
        peak_value = peak_value- baseline
        peak_snr = np.abs(peak_value/mea_mad)
        
        # evrything in Dataframe
        gt_info.at[rec_name, 'nb_spike'] = gt_indexes.size
        gt_info.at[rec_name, 'max_on_channel'] = max_on_channel
        gt_info.at[rec_name, 'peak_value'] = peak_value
        gt_info.at[rec_name, 'peak_snr'] = peak_snr
        gt_info.at[rec_name, 'noise_mad'] = mea_mad
        
        
        fig, ax = plt.subplots()
        ax.plot(wf_median.T.flatten())
        fig.savefig(gt_folder+'GT waveforms flatten.png')

        fig, ax = plt.subplots()
        ax.plot(wf_median)
        ax.axvline(-n_left)
        fig.savefig(gt_folder+'GT waveforms.png')
        
        
    gt_info.to_excel(ground_truth_folder+'gt_info.xlsx')



if __name__ == '__main__':
    unzip_all()
    detect_ground_truth_spike_on_juxta()
