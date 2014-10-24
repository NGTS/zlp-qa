#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import numpy as np
from qa_common import plt, get_logger
from qa_common.airmass_correct import remove_extinction
from qa_common.filter_objects import good_measurement_indices
import matplotlib.colors as colors
import matplotlib.cm as cmx
import fitsio
from scipy.optimize import leastsq
import argparse
from collections import namedtuple
import multiprocessing as mp
from functools import partial
import logging

NoiseResult = namedtuple('NoiseResult', ['x', 'y', 'yerr', 'white'])

logger = get_logger(__file__)


class NullPool(object):

    def __init__(self, *args, **kwargs):
        pass

    def map(self, fn, l):
        return map(fn, l)


def main(args):
    filename = args.filename
    data_dict = load_data(filename)

    left_edges = 10 ** np.linspace(2, 5, 10)[:-1]
    right_edges = 10 ** (np.log10(left_edges) + 3. / 9.)

    values = range(0, len(left_edges) + 1)

    mymap = cm = plt.get_cmap('autumn')
    cNorm = colors.Normalize(vmin=0, vmax=values[-1])
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=mymap)

    levels = np.array([left_edges[0]] + list(right_edges))

    if args.serial:
        pool_class = NullPool
    else:
        pool_class = mp.Pool

    fig, axis = plt.subplots()

    flux_limits = [(left_edges[i], right_edges[i]) for i in
                   xrange(len(left_edges))]
    fn = partial(noisecharacterise, datadict=data_dict,
                 flux_limits=flux_limits,
                 ax=axis)

    pool = pool_class()
    plot_data = pool.map(fn, range(0, len(left_edges)))

    for i, r in enumerate(plot_data):
        colorVal = scalarMap.to_rgba(values[i])
        axis.errorbar(r.x, r.y, r.yerr, color=colorVal, linewidth=2.0)
        axis.plot(r.x, r.white, '--', color='grey', alpha=0.8)

    cbar = create_colourbar(fig, values, mymap, cNorm)
    nicelist = [int(left_edges[0])] + [int(x) for x in right_edges]
    cbar.ax.set_yticklabels(nicelist[::-1])  # vertically oriented colorbar

    axis.set_yscale('log')
    axis.set_xscale('log')
    axis.set_xlabel("Bin size (Minutes)")
    axis.set_ylabel("Fractional RMS (millimags)")
    axis.set_yticks((0.5, 1, 2, 5, 10, 20, 50, 100))
    axis.set_yticklabels(('0.5', '1', '2', '5', '10', '20', '50', '100'))
    axis.set_xticks((1, 5, 10, 60))
    axis.set_xticklabels(('1', '5', '10', '60'))

    fig.tight_layout()
    if args.output is not None:
        plt.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()


def create_colourbar(fig, values, mymap, cNorm):
    ax = fig.get_axes()[0]
    Z = [[0, 0], [0, 0]]
    CS3 = ax.contourf(Z, values[::-1], norm=cNorm, cmap=mymap)
    cbar = fig.colorbar(CS3, ticks=values[::-1])
    return cbar


def load_data(filename, mask=[]):
    dateclip = datesplit(filename)

    with fitsio.FITS(filename) as infile:
        imagelist = infile['imagelist']
        tmid = imagelist['tmid'].read()
        meanbias = imagelist['meanbias'].read()
        airmass = imagelist['airmass'].read()
        shift = imagelist['shift'].read()
        clouds = imagelist['clouds'].read()
        T = imagelist['T'].read()
        exposure = imagelist['exposure'].read()

        flux = infile['flux'].read()

        catalogue = infile['catalogue']
        mean_fluxes = catalogue['flux_mean'].read()

        ccdx = infile['ccdx'][:, :1].flatten()
        ccdy = infile['ccdy'][:, :1].flatten()

    # Normalise by exposure time
    flux /= exposure

    # Filter out bad points
    per_object_ind, per_image_ind = good_measurement_indices(shift, clouds,
                                                             airmass,
                                                             ccdx, ccdy)
    initial_shape = flux.shape
    flux = flux[per_object_ind][:, per_image_ind]
    mean_fluxes = mean_fluxes[per_object_ind]
    airmass = airmass[per_image_ind]
    tmid = tmid[per_image_ind]

    logger.info('Flux array shape', initial=initial_shape,
                final=flux.shape)
    logger.debug('Removing extinction')
    flux = remove_extinction(flux, airmass,
                             flux_min=1E4,
                             flux_max=6E5)

    logger.info('Nights in data', nights=dateclip[:, 0])

    if len(mask) > 0:
        dateclip = dateclip[mask]
    logger.info("Number of nights used", nights=dateclip[:, 0])

    cut = []
    for time in tmid:
        clip = [((time > date[0]) & (time < date[1])) for date in dateclip]
        cut += [any(clip)]
    cut = np.array(cut)

    tmid = tmid[cut]
    flux = flux[:, cut]

    outdict = {'time': tmid, 'flux': flux, 'mean_fluxes': mean_fluxes[
        cut], 'meanbias': meanbias[cut], 'T': T[cut]}

    return outdict


def noisecharacterise(i, flux_limits, datadict, c='b', model=True, ax=None):
    '''Characterises the noise level of bright, non saturated stars from the 
    output of sysrem as a function of number of bins'''
    ax = ax if ax is not None else plt.gca()

    tmid = datadict['time']

    cadence = np.median(np.diff(tmid)) * 24 * 60

    flux = datadict['flux']

    binlow = 0.2
    binhigh = 4.0

    binstep = 0.1

    binrange = [int(np.ceil(10.0 ** (x)))
                for x in np.arange(binlow, binhigh, binstep)]

    binrange = np.sort(np.array(list(set(binrange))))

    binrange = binrange[binrange < len(flux[0]) / 3]

    minflux, maxflux = flux_limits[i]

    zero = 21.18135675

    mag_min = zero - 2.512 * np.log10(maxflux)
    mag_max = zero - 2.512 * np.log10(minflux)
    rms_lim = 1e9

    avflux = np.median(flux, axis=1)
    stdflux = np.std(flux, axis=1)
    rms = stdflux
    rms = abs(1.0857 * 1000.0 * stdflux / avflux)
    new_logger = logger.bind(average=avflux, std=stdflux, rms=rms)

    sane_keys = [((rms != np.inf) & (avflux != np.inf) & (rms != 0) & (rms < rms_lim) & (
        avflux != 0) & (rms != np.NaN) & (avflux != np.NaN) & (avflux < maxflux) & (avflux > minflux))]

    flux_sane = flux[sane_keys].copy()

    new_logger = new_logger.bind(nstars=len(flux_sane),
                                 mag_min=mag_min, mag_max=mag_max,
                                 npoints=len(flux_sane[0]))
    new_logger.info('Stats')

    logger.debug('median flux range',
                 min_value=min(np.median(flux_sane, axis=1)),
                 max_value=max(np.median(flux_sane, axis=1)))

    median_list = [np.median(rms[sane_keys])]
    N_bin_list = [1]
    quartiles = [
        [np.percentile(rms[sane_keys], 25), np.percentile(rms[sane_keys], 75)]]
    rms_error = [
        (np.std(rms[sane_keys])) / np.sqrt(len(rms[sane_keys]) * 1000)]

    for N in binrange:

        logger.debug('bin size', value=N)

        binned = binning(flux_sane, N)

        avflux = np.median(binned, axis=1)
        stdflux = np.std(binned, axis=1)
        rms = stdflux
        rms = abs(1.0857 * 1000.0 * stdflux / avflux)

        sanity = ((rms != np.inf) & (avflux != np.inf) & (rms != 0) & (avflux != 0) & (
            rms != np.NaN) & (avflux != np.NaN) & (avflux < maxflux) & (avflux > minflux))
        rmssane = rms[sanity]
        median_list += [np.median(rmssane)]
        quartiles += [[np.percentile(rmssane, 25), np.percentile(rmssane, 75)]]
        N_bin_list += [N]
        rms_error += [(np.std(rms[sanity])) / np.sqrt(1000 * len(rms[sanity]))]

    prior = [median_list[0], median_list[-1]]

    N_bin_list = np.array(N_bin_list)
    median_list = np.array(median_list)
    rms_error = np.array(rms_error)
    quartiles = np.array(quartiles)

    low_quart = quartiles[:, 0]
    high_quart = quartiles[:, 1]

    m = 15

    output = leastsq(
        fitnoise, prior, args=(N_bin_list[:m], median_list[:m], rms_error[:m]))

    final = output[0]

    noise_curve = noisemodel(final, N_bin_list)
    white_curve = noisemodel([final[0], 0], N_bin_list)
    red_curve = noisemodel([0, final[1]], N_bin_list)

    return NoiseResult(
        cadence * N_bin_list,
        median_list,
        rms_error,
        white_curve)


def datesplit(filename):
    '''returns an array index that can be used a cut an output file in desired
    dateranges'''
    time = fitsio.read(filename, 'imagelist')['TMID']
    nights_used = [time[0]]
    for i in range(1, len(time)):
        shift = time[i] - time[i - 1]
        if shift > 0.5:
            nights_used += [time[i]]

    nights_used += [1e9]

    nights_used = np.array(nights_used)

    dateclip = []
    for i in range(len(nights_used) - 1):
        dateclip += [nights_used[i:i + 2]]
    dateclip = np.array(dateclip)

    return dateclip


def binning(series, bin):
    '''bins a time series to the level specified by `bin`'''
    bins = np.floor(len(series[0, :]) / bin)

    binned = []

    length = len(series[:, 0])

    binned = np.zeros((length, bins))

    for i in np.arange(0, length):
        for x in np.arange(0, bins):
            place = x * bin

            summ = 0

            for y in range(0, bin):
                summ += series[i, place + y]

            binned[i, x] = summ / bin

    return binned


def fitnoise(x, N, data, error):
    noise = noisemodel(x, N)
    return (noise - data) / error


def noisemodel(x, N):

    white = x[0]
    red = x[1]

    curve = ((white * N ** -0.5) ** 2.0 + red ** 2.0) ** 0.5

    return curve

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', help='Save to output file',
                        required=False)
    parser.add_argument('--serial', help='Do not use parallel processing',
                        action='store_true', default=False)
    main(parser.parse_args())
