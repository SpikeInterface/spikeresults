# Comparison of spike sorters with MEArec and SpikeInterface

The `mearec-gt-comparison.ipynb` notebook reproduces the plots in Figure 4 of the [SpikeInterface paper](https://www.biorxiv.org/content/10.1101/796599v1).

Dataset generated with [MEArec](https://github.com/alejoe91/MEArec) (author: Alessio Paolo Buccino).

The recordings are simulated on a **SqMEA-10-15** probe, with 100 channels in a 10x10 configurtion, and with an inter-electrode distance of 15 um. There are 50 ground-truth neurons and the duration is 60 seconds.

The file **recordings_50cells_SqMEA-10-15um_60.0_10.0uV_27-03-2019_13_31.h5** is freely downloadable [here](https://doi.org/10.5281/zenodo.3260283). You can download the file, unzip it in this folder, and run the notebook.

This notebook is a demonstration of the SpikeInterface ground-truth comparison framework.
The notebook launches several popular sorters on the recording and computes several performance metrics.
