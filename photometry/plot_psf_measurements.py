#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from qa_common.plotting import plt
from qa_common import get_logger
import csv
import numpy as np
import itertools
from functools import partial

logger = get_logger(__file__)

psf_indices = [1, 3, 5, 7, 9]
psf_types = ['T', 'A', 'B']
psf_keys = ['psf_{typ}_{i}'.format(typ=typ,
                                   i=i)
            for (typ, i) in itertools.product(psf_types, psf_indices)]

markersize = 3.

colours = {
        1: '#F5374D',
        3: '#84E533',
        5: 'k',
        7: '#365BB0',
        9: '#AB26AB',
        }


def random_zorder(x, y, nvalues, min_zorder=10):
    order = np.random.randint(min_zorder, min_zorder + nvalues,
            size=x.size)
    for zorder in np.sort(np.unique(order)):
        ind = order == zorder
        yield (x[ind], y[ind], zorder)

def compute_stats(data):
    data = np.array(data)
    low, high = np.percentile(data, [16, 84], axis=0)
    mean = data.mean(axis=0)
    return mean - low, mean, high - mean


def render(ax, mjd, data, key_type):
    zorder_min = 10
    stack = []
    for key in psf_keys:
        if key_type in key:
            index = int(key.split('_')[-1])
            colour = colours[index]
            for (x, y, zorder) in random_zorder(mjd, data[key], len(psf_indices)):
                ax.plot(x, y, '.', color=colour, label=key, zorder=zorder,
                        markersize=markersize)
            stack.append(data[key])
    # low, med, high = compute_stats(np.array(stack))
    # _errorbar(ax, mjd, med, low, high)


def main(args):
    data = np.genfromtxt(args.data, delimiter=',', names=True)

    mjd = data['mjd']
    mjd0 = int(mjd.min())
    mjd -= mjd0

    fig, axes = plt.subplots(5, 1, sharex=True)
    render(axes[1], mjd, data, key_type='A')
    render(axes[2], mjd, data, key_type='B')
    render(axes[3], mjd, data, key_type='T')

    stack = []
    for i in psf_indices:
        A = data['psf_A_{}'.format(i)]
        B = data['psf_B_{}'.format(i)]
        fwhm = (A + B) / 2.
        for (x, y, zorder) in random_zorder(mjd, fwhm, len(psf_indices)):
            axes[0].plot(x, y, '.', zorder=zorder, color=colours[i],
                    markersize=markersize)
        e = np.sqrt(1. - (B / A) ** 2)
        stack.append(e)
        for (x, y, zorder) in random_zorder(mjd, e, len(psf_indices)):
            axes[4].plot(x, y, '.', color=colours[i],
                    zorder=zorder, label='Ecc. {}'.format(i),
                    markersize=markersize)
    low, med, high = compute_stats(stack)
    # _errorbar(axes[4], mjd, med, low, high)

    labels = [r'$\mathrm{fwhm}$', r'$a$', r'$b$', r'$\theta$', r'$e$']
    for (ax, label) in zip(axes, labels):
        ax.grid(True)
        ax.set_ylabel(label)

    axes[-2].set_ylim(-360, 360)
    axes[-1].set_xlabel(r'MJD - {}'.format(mjd0))

    fig.tight_layout()
    fig.savefig(args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=argparse.FileType(mode='r'), default='-')
    parser.add_argument('-o', '--output',
                        required=False,
                        type=argparse.FileType(mode='w'),
                        default='-')
    main(parser.parse_args())
