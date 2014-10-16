import matplotlib.pyplot as plt
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


def masked_log10(data, *args, **kwargs):
    '''
    Given an array of data with possible bad values, e.g. < 0 or nans build
    a masked array from the data, then compute the log10 of this dataset.
    '''
    good_values = (np.isfinite(data)) & (data > 0)
    masked_data = np.ma.masked_where(~good_values, data)
    return np.ma.log10(masked_data)


def compute_bulk_standard_lightcurve(mags, ind):
    standards = mags[ind]
    normalised_standards = (standards.T - np.median(standards, axis=1)).T
    return np.median(normalised_standards, axis=0)


def compute_standards_index(data, flux_min, flux_max):
    med_flux = np.median(data, axis=1)
    if flux_min is not None and flux_max is not None:
        ind = (med_flux >= flux_min) & (med_flux <= flux_max)
    elif flux_min is not None:
        ind = med_flux >= flux_min
    elif flux_max is not None:
        ind = med_flux <= flux_max
    else:
        ind = np.ones_like(med_flux, dtype=bool)

    return ind


def fit_airmass_trend(airmass, standard):
    good_ind = np.isfinite(standard)
    return np.poly1d(np.polyfit(airmass[good_ind], standard[good_ind], 1))

def mags_to_flux(mags, zp=0.):
    return 10 ** ((zp - mags) / 2.5)

def remove_extinction(data, airmass, flux_min=None, flux_max=None):
    '''
    Given a flux array and airmass time series, perform the following steps:

        * optionally build a subgroup of stars
        * build a bulk lightcurve
        * fit an airmass coefficient to this data set
        * return a new dataset with the same dimensions as the input but
            without extinction

    Inputs:
        * NxM array of flux measurements
        * airmass time series of length M
        * optionally min and max to select standard stars

    Returns:
        * NxM array of extinction-corrected flux measurements


    The algorithm works in flux space so negative fluxes are ok.
    '''
    standards_ind = compute_standards_index(data, flux_min, flux_max)
    instrumental_mags = -2.5 * masked_log10(data)
    bulk_standard = compute_bulk_standard_lightcurve(instrumental_mags,
                                                     standards_ind)

    fit = fit_airmass_trend(airmass, bulk_standard)
    correction_factor = mags_to_flux(fit.c[0] * airmass)

    return data / correction_factor
