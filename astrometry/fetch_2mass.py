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

class Catalogue(object):
    def __init__(self, ra, dec, radius=3.0, max_objects=1E6):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ra = ra
        self.dec = dec
        self.radius = radius
        self.max_objects = int(max_objects)

        self.logger.info("Searching in a radius of {radius} degrees "
                "around position ({ra},{dec})".format(
                    radius=self.radius,
                    ra=self.ra,
                    dec=self.dec))

    def build(self, output_filename):
        ra = str(self.ra)
        dec = '+{}'.format(self.dec) if self.dec > 0 else '-{}'.format(self.dec)

        cmd = map(str, ['find2mass',
            ra, dec,
            '-m', self.max_objects,
            '-rd', self.radius])

        self.logger.debug("Running command [{}]".format(' '.join(cmd)))
        output = sp.check_output(cmd, stderr=sp.PIPE)

        with open(output_filename, 'w') as outfile:
            keys = ['ra', 'dec', 'jmag']
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()

            for line in output.split("\n"):
                if line and '#' not in line:
                    data = self.extract_all(line)

                    writer.writerow(data)


    @staticmethod
    def _extract(line, beginning, end):
        return line[beginning:end]

    def extract_ra(self, line):
        return float(self._extract(line, 0, 10))

    def extract_dec(self, line):
        return float(self._extract(line, 12, 21))

    def extract_jmag(self, line):
        return float(self._extract(line, 54, 60))

    def extract_all(self, line):
        ra = self.extract_ra(line)
        dec = self.extract_dec(line)
        jmag = self.extract_jmag(line)

        return {'ra': ra,
                'dec': dec,
                'jmag': jmag,
                }


def build_catalogue(input_filename, output_filename):
    with fitsio.FITS(input_filename) as infile:
        data = zip(*infile[1]['RA', 'DEC'].read())

    ra, dec = map(np.degrees, data)
    av_ra = np.average(ra)
    av_dec = np.average(dec)

    catalogue = Catalogue(av_ra, av_dec).build(output_filename)


def main(args):
    logger.debug('Matching from {}'.format(args.catalogue))
    logger.debug('Rendering to output file {}'.format(args.output))
    build_catalogue(args.catalogue, args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('catalogue', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())
