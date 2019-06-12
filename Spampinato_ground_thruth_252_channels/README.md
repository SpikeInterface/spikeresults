# Ground truth recordings for validation of spike sorting algorithms


Spampinato from Institut de la Vision have publish data from mice retina recorded with from dense array.
The data contain one ground truth to benchmark spike sorting tools.

Here the official publication of this open dataset:
https://zenodo.org/record/1205233#.W9mq1HWLTIF


This datasets was used by Pierre Yger publish spyking circus:
https://elifesciences.org/articles/34518


Here 2 notebooks:
  * **prepare_and_check_ground_truth.py.ipynb**: prepare files, detect juxta cellular and check validity
  * **sorter_comparison.ipynb** : comparison of severals sorters on this datasets

that compare some sorter on theses recording.

Each recording have several units and **one** of theses have a ground truth recorded with juxta cellular.
The SNR on MEA is differents on each file so we can easily compare the false positive and true positive score by sorter and SNR.




