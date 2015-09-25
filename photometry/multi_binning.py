#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from qa_common import get_logger
from qa_common.plotting import plt
from qa_common.filter_objects import good_measurement_indices
from qa_common.util import NullPool
import matplotlib.colors as colors
import matplotlib.cm as cmx
import fitsio
from scipy.optimize import leastsq
import argparse
from collections import namedtuple
import multiprocessing as mp
from functools import partial
import logging
from scipy import stats
import sqlite3

NoiseResult = namedtuple('NoiseResult', ['x', 'y', 'yerr', 'white'])

logger = get_logger(__file__)



class NoiseResultRenderer(object):
    def __init__(self, results, night, camera_id):
        self.results = results
        self.night = night
        self.camera_id = camera_id

        self.tablename = 'results'

    def save(self, filename):
        logger.info("Rendering")
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()
            self.run_query(cursor, self.drop_db_query())
            self.run_query(cursor, self.create_db_query())
            self.addrows(cursor)
            connection.commit()

    def addrows(self, cursor):
        print('Uploading')
        query = '''insert into {self.tablename} (
        night, left_edge, right_edge, bin_value, frms_binned, expected_white,
        bin_index, camera_id)
        values (?, ?, ?, ?, ?, ?, ?, ?)'''.format(self=self)
        cursor.executemany(query, self.items)

    @property
    def items(self):
        for i, (ledge, redge, bin_stats) in enumerate(self.results):
            for (bin_value, frms_binned, _, expected_white) in zip(*bin_stats):
                yield (self.night, ledge, redge, bin_value, frms_binned,
                       expected_white, i, int(self.camera_id))

    def run_query(self, cursor, query_str, params=None):
        logger.debug(query_str.replace('\n', ''))
        if params:
            cursor.execute(query_str, params)
        else:
            cursor.execute(query_str)

    def drop_db_query(self):
        return '''drop table if exists {self.tablename}'''.format(self=self)

    def create_db_query(self):
        return '''
    create table {self.tablename} (
    id integer primary key,
    camera_id integer not null,
    night string not null,
    left_edge float not null,
    right_edge float not null,
    bin_value integer not null,
    frms_binned float not null,
    expected_white float not null,
    bin_index integer not null,
    unique(camera_id, night) on conflict replace
    )'''.format(self=self)




def main(args):
    filename = args.filename
    data_dict = load_data(filename, hdu=args.hdu)

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

    plot_data = extract_plot_data(left_edges, right_edges, data_dict, pool_class)
    plot_data_sorted = sorted(plot_data, key=lambda row: row[0])
    if args.render:
        r = NoiseResultRenderer(plot_data_sorted, night=data_dict['night'],
                                camera_id=data_dict['camera_id'])
        r.save(args.render)

    for i, (_, _, r) in enumerate(plot_data):
        colorVal = scalarMap.to_rgba(values[i])
        axis.plot(r.x, r.y, color=colorVal, linewidth=2.0)
        # axis.errorbar(r.x, r.y, r.yerr, color=colorVal, linewidth=2.0)
        axis.plot(r.x, r.white, '--', color='grey', alpha=0.8)



    cbar = create_colourbar(fig, values, mymap, cNorm)
    nicelist = [int(left_edges[0])] + [int(x) for x in right_edges]
    cbar.ax.set_yticklabels(nicelist[::-1])  # vertically oriented colorbar

    axis.set(yscale='log',
            xscale='log',
            xlabel="Bin size (Minutes)",
            ylabel="Fractional RMS (millimags)",
            title=':'.join([os.path.basename(args.filename), args.hdu]),
            yticks=(0.5, 1, 2, 5, 10, 20, 50, 100),
            yticklabels=('0.5', '1', '2', '5', '10', '20', '50', '100'),
            xticks=(1, 5, 10, 60),
            xticklabels=('1', '5', '10', '60'))
    axis.set(xlim=(0.1, 150), ylim=(0.1, 100))

    fig.tight_layout()
    if args.output is not None:
        plt.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()


def extract_plot_data(left_edges, right_edges, data_dict,
                      pool_class):
    flux_limits = [(left_edges[i], right_edges[i]) for i in
                   xrange(len(left_edges))]
    fn = partial(noisecharacterise, datadict=data_dict,
                 flux_limits=flux_limits, ax=None)

    pool = pool_class()
    return pool.map(fn, range(0, len(left_edges)))




def create_colourbar(fig, values, mymap, cNorm):
    ax = fig.get_axes()[0]
    Z = [[0, 0], [0, 0]]
    CS3 = ax.contourf(Z, values[::-1], norm=cNorm, cmap=mymap)
    cbar = fig.colorbar(CS3, ticks=values[::-1])
    return cbar


def load_data(filename, hdu, mask=None):
    mask = mask if mask is not None else []

    dateclip = datesplit(filename)

    with fitsio.FITS(filename) as infile:
        imagelist = infile['imagelist']
        night = imagelist['night'].read()[0]
        camera_id = imagelist['cameraid'].read()[0]
        tmid = imagelist['tmid'].read()
        airmass = imagelist['airmass'].read()
        exposure = imagelist['exposure'].read()

        flux = infile[hdu].read()

        catalogue = infile['catalogue']
        mean_fluxes = catalogue['flux_mean'].read()

        ccdx = infile['ccdx'][:, :1].flatten()
        ccdy = infile['ccdy'][:, :1].flatten()


    # Normalise by exposure time
    flux /= exposure

    logger.info('Nights in data: %s', dateclip[:, 0])

    if len(mask) > 0:
        dateclip = dateclip[mask]
    logger.info("Number of nights used: %s", dateclip[:, 0])

    cut = []
    for time in tmid:
        clip = [((time > date[0]) & (time < date[1])) for date in dateclip]
        cut += [any(clip)]
    cut = np.array(cut)

    tmid = tmid[cut]
    flux = flux[:, cut]

    outdict = {'time': tmid, 'flux': flux, 'mean_fluxes': mean_fluxes[cut],
               'night': night, 'camera_id': camera_id} 

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
    # Fractional rms in units of mmag
    rms = abs(1.0857 * 1000.0 * stdflux / avflux)

    sane_keys = ((rms > 0) &
                 (avflux > 0) &
                 (avflux < maxflux) &
                 (avflux > minflux))

    flux_sane = flux[sane_keys].copy()

    logger.info('Stats: av: %s, std: %s, rms: %s', avflux, stdflux, rms)
    logger.debug('nstars: %s, mag_min: %s, mag_max: %s, npoints: %s',
                 len(flux_sane), mag_min, mag_max, len(flux_sane[0]))

    logger.debug('median flux range: %s to %s',
                 min(np.median(flux_sane, axis=1)),
                 max(np.median(flux_sane, axis=1)))

    median_list = [np.median(rms[sane_keys])]
    N_bin_list = [1]
    quartiles = [
        [np.percentile(rms[sane_keys], 25), np.percentile(rms[sane_keys], 75)]]
    rms_error = [
        (np.std(rms[sane_keys])) / np.sqrt(len(rms[sane_keys]) * 1000)]

    for N in binrange:

        logger.debug('bin size: %s', N)

        binned = binning(flux_sane, N)

        avflux = np.median(binned, axis=1)
        stdflux = np.std(binned, axis=1)
        rms = stdflux
        rms = abs(1.0857 * 1000.0 * stdflux / avflux)

        sanity = ((avflux < maxflux) & (avflux > minflux))

        rmssane = rms[sanity]
        median_list += [np.median(rmssane)]
        quartiles += [[np.percentile(rmssane, 25), np.percentile(rmssane, 75)]]
        N_bin_list += [N]
        rms_error += [(np.std(rms[sanity])) / np.sqrt(rms[sanity].size)]

    # Get the limits of the median list
    prior = [median_list[0], median_list[-1]]

    # Convert to numpy arrays
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

    return minflux, maxflux, NoiseResult(
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
    logger.debug('Binning')
    bins = np.floor(len(series[0, :]) / bin)
    x = np.arange(series.shape[1])

    binned = []
    for lc in series:
        by, _, _ = stats.binned_statistic(
            x, lc, bins=bins, statistic='median')
        binned.append(by)
    binned = np.array(binned)

    logger.debug('Binning complete')

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
    parser.add_argument('-r', '--render', required=False,
                        help='Save extracted noise results to file')
    parser.add_argument('--serial', help='Do not use parallel processing',
                        action='store_true', default=False)
    parser.add_argument('-H', '--hdu', required=True,
            help='HDU to plot')
    try:
        main(parser.parse_args())
    except Exception as e:
        logger.exception('Failure')
        sys.exit(0)
