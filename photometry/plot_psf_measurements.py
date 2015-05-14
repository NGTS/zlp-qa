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

psf_indices = list(range(1, 10))
psf_types = ['T', 'A', 'B']
psf_keys = ['psf_{typ}_{i}'.format(typ=typ,
                                   i=i)
            for (typ, i) in itertools.product(psf_types, psf_indices)]


def _errorbar(ax, x, y, low, high):
    ax.errorbar(x, y, [low, high], color='k', marker='o', ls='None', capsize=0.)


def compute_stats(data):
    data = np.array(data)
    low, high = np.percentile(data, [16, 84], axis=0)
    mean = data.mean(axis=0)
    return mean - low, mean, high - mean


def render(ax, mjd, data, key_type):
    stack = []
    for key in psf_keys:
        if key_type in key:
            ax.plot(mjd, data[key], '.', label=key, alpha=0.5)
            stack.append(data[key])
    low, med, high = compute_stats(np.array(stack))
    _errorbar(ax, mjd, med, low, high)


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
        axes[0].plot(mjd, fwhm, '.')
        e = np.sqrt(1. - (B / A) ** 2)
        stack.append(e)
        axes[4].plot(mjd, e, '.', label='Ecc. {}'.format(i), alpha=0.5)
    low, med, high = compute_stats(stack)
    _errorbar(axes[4], mjd, med, low, high)

    labels = ['fwhm', 'a', 'b', r'$\theta$', 'e']
    for (ax, label) in zip(axes, labels):
        ax.grid(True)
        ax.set_ylabel(label)

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
