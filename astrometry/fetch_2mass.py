#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import subprocess as sp
import fitsio
import numpy as np
import tempfile
import csv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Stilts(object):
    stilts_file = os.path.join(os.path.dirname(__file__),
            'stilts.jar')
    service_url = 'http://wfaudata.roe.ac.uk/twomass-dsa/DirectCone?DSACAT=TWOMASS&DSATAB=twomass_psc&'

    def __init__(self):
        self.command = ['java', '-jar', self.stilts_file, ]

    def build_command(self, *args, **kwargs):
        cmd = self.command[:]
        cmd.extend(args)
        for key, value in kwargs.iteritems():
            cmd.append('{}={}'.format(key, value))

        cmd = map(str, cmd)

        logger.debug('Running command: [{}]'.format(' '.join(cmd)))

        return cmd

    def run_command(self, *args, **kwargs):
        sp.check_call(self.build_command(*args, **kwargs))

    @classmethod
    def run(cls, *args, **kwargs):
        self = cls()
        self.run_command(*args, **kwargs)

def build_catalogue(input_filename, output_filename, sr):
    with fitsio.FITS(input_filename) as infile:
        data = zip(*infile[1]['RA', 'DEC'].read())

    ra, dec = map(np.degrees, data)
    av_ra = np.average(ra)
    av_dec = np.average(dec)

    with tempfile.NamedTemporaryFile(suffix='.csv') as tfile:
        logger.debug("Using temporary catalogue {}".format(tfile.name))
        writer = csv.DictWriter(tfile, fieldnames=['ra', 'dec'])
        writer.writeheader()
        writer.writerow({'ra': av_ra, 'dec': av_dec})

        tfile.seek(0)

        logger.debug("Querying position ({},{})".format(av_ra, av_dec))
        Stilts.run('coneskymatch', 'in={}'.format(tfile.name), 
                ra='ra', dec='dec', sr=sr,
                ifmt='csv',
                serviceurl=Stilts.service_url,
                out=output_filename)


def main(args):
    logger.debug('Matching from {}'.format(args.catalogue))
    logger.debug('Rendering to output file {}'.format(args.output))
    build_catalogue(args.catalogue, args.output, sr=1.5)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('catalogue', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())
