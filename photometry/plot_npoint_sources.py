#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from qa_common.plotting import plt
from qa_common import plot_night_breaks, get_logger
import csv
import numpy as np

logger = get_logger(__file__)


def main(args):
    reader = csv.DictReader(args.data)
    mjd, nsources = map(np.array, zip(*[(float(row['mjd']), float(row['nsources']))
                                        for row in reader]))
    error = np.sqrt(nsources)

    mjd0 = int(mjd.min())
    mjd -= mjd0

    fig, axis = plt.subplots()
    axis.errorbar(mjd, nsources, error, ls='', marker='', capsize=0., lw=1.,
            alpha=0.5, color='k')
    axis.plot(mjd, nsources, 'k.')
    axis.set_xlabel(r'MJD - {}'.format(mjd0))
    axis.set_ylabel(r'Number of point sources')
    axis.grid(True)
    fig.tight_layout()

    fig.savefig(args.output, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=argparse.FileType(mode='r'), default='-')
    parser.add_argument('-o', '--output',
                        required=False,
                        type=argparse.FileType(mode='w'),
                        default='-')
    main(parser.parse_args())
