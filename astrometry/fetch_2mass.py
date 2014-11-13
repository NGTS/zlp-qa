#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess as sp
import fitsio
import numpy as np
import tempfile
import csv
from qa_common import get_logger

logger = get_logger(__file__)

class Catalogue(object):
    def __init__(self, ra, dec, box_width=3, max_objects=1E6):
        self.ra = ra
        self.dec = dec
        self.box_width = box_width
        self.max_objects = int(max_objects)

        logger.info('Searching in box',
                    ra=self.ra,
                    dec=self.dec,
                    box_width=self.box_width)

    def build(self, output_filename):
        ra = str(self.ra)
        dec = '+{}'.format(self.dec) if self.dec > 0 else '-{}'.format(self.dec)

        cmd = map(str, ['find2mass',
            ra, dec,
            '-m', self.max_objects,
            '-bd', self.box_width])

        logger.debug("Running command: %s", ' '.join(cmd)
        output = sp.check_output(cmd, stderr=sp.PIPE)

        with open(output_filename, 'w') as outfile:
            keys = ['ra', 'dec', 'jmag', 'name_2mass']
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
    
    def extract_name(self, line):
        return self._extract(line, 36, 52)

    def extract_all(self, line):
        ra = self.extract_ra(line)
        dec = self.extract_dec(line)
        jmag = self.extract_jmag(line)
        name = self.extract_name(line)

        return {'ra': ra,
                'dec': dec,
                'jmag': jmag,
                'name_2mass': name,
                }


def build_catalogue(input_filename, output_filename):
    with fitsio.FITS(input_filename) as infile:
        data = zip(*infile[1]['RA', 'DEC'].read())

    ra, dec = map(np.degrees, data)
    av_ra = np.average(ra)
    av_dec = np.average(dec)

    catalogue = Catalogue(av_ra, av_dec).build(output_filename)


def main(args):
    logger.debug('Matching from catalogue %s', args.catalogue)
    logger.debug('Output file: %s', output)
    build_catalogue(args.catalogue, args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('catalogue', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())
