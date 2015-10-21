#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from qa_common.plotting import plt
from qa_common import get_logger
from astropy.io import fits
import numpy as np
import pymysql
from pymysql.cursors import DictCursor
from astropy.time import Time
from collections import namedtuple

logger = get_logger(__file__)

ESOStats = namedtuple('ESOStats', ['mjd', 'seeing', 'tau', 'theta'])


def extract_time_range(filename):
    '''
    Given a fits file, return the two datetimes representing the range of
    observations
    '''

    with fits.open(filename) as infile:
        imagelist = infile['imagelist'].data

    mjd = imagelist['tmid']
    times = Time(mjd, format='mjd')
    return times.datetime.min(), times.datetime.max()


def fetch_eso_stats(start_time, end_time):
    query = '''select * from eso_paranal_ambient
    where night between %s and %s'''

    with pymysql.connect(user='sw',
                         host='ngtsdb',
                         db='swdb',
                         cursorclass=DictCursor) as cursor:
        cursor.execute(query, (start_time, end_time))
        rows = cursor.fetchall()

    get_key = lambda key: np.array([row[key] for row in rows])

    time = Time(get_key('night'))
    mjd = time.mjd

    return ESOStats(mjd=mjd,
                    seeing=get_key('seeing'),
                    tau=get_key('tau0'),
                    theta=get_key('theta0'))


def main(args):
    logger.info('Extracting night')
    time_range = extract_time_range(args.filename)
    logger.info('Querying between %s and %s', *time_range)

    eso_stats = fetch_eso_stats(*time_range)
    mjd0 = int(eso_stats.mjd.min())

    fig, axes = plt.subplots(3, 1, sharex=True)
    for (axis, key) in zip(axes, ['seeing', 'tau', 'theta']):
        axis.plot(eso_stats.mjd - mjd0, getattr(eso_stats, key), '.')
        axis.set(ylabel=key.capitalize())
    axes[-1].set(xlabel='MJD - {}'.format(mjd0))
    fig.tight_layout()
    fig.savefig(args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o',
                        '--output',
                        required=False,
                        type=argparse.FileType(mode='w'),
                        default='-')
    main(parser.parse_args())
