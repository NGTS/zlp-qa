import numpy as np


def low_shift_index(shift, initial_bad_shift_point=3, nsigma=5):
    '''
    Iteratively remove outliers
    '''
    ind = shift <= initial_bad_shift_point
    initial_good_shift = shift[ind]

    med_shift = np.median(initial_good_shift)
    std_shift = np.std(initial_good_shift)

    return shift <= med_shift + nsigma * std_shift


def good_measurement_indices(shift, clouds, airmass, ccdx, ccdy,
                             ccd_margin=4, max_airmass=2.):
    '''
    Remove some known reasons why lightcurve(s) may be bad. These are:
        * high shift value suggesting large jumps in the frame
        * measurable cloudy data
        * high airmass measurements
        * aperture positions near the edge of the chip

    This is temporary until proper flagging takes place.
    '''
    good_shift_ind = low_shift_index(shift)
    ccd_ind = ((ccdx > ccd_margin) &
               (ccdx < 2048 - ccd_margin) &
               (ccdy > ccd_margin) &
               (ccdy < 2048 - ccd_margin))
    airmass_ind = airmass <= max_airmass

    per_object_ind = ccd_ind
    per_image_ind = good_shift_ind & airmass_ind

    return per_object_ind, per_image_ind
