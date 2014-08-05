import numpy as np

def find_night_breaks(mjd, gap_size=0.3):
    mjd_a = np.array(mjd)
    frames = np.arange(mjd_a.size)
    ind = np.diff(mjd_a) > gap_size
    return frames[ind]

