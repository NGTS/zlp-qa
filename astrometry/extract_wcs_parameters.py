#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import fitsio
from astropy import wcs

class Extracted(object):
    keys = ['fname', 'mjd', 'cmd_ra', 'cmd_dec',
            'tel_ra', 'tel_dec', 'crval1', 'crval2', 'cd1_1', 'cd1_2',
            'cd2_1', 'cd2_2', 'pv2_1', 'pv2_3', 'pv2_5',
            'skylevel', 'skynoise', 'numbrms', 'stdcrms']
    wcs_keys = ['solved_ra', 'solved_dec']

    all_keys = keys + wcs_keys

    def __init__(self, fname):
        self.fname = fname

    def writerow(self, writer):
        writer.writerow(self.extract_data())

    def extract_data(self):
        self.header = fitsio.read_header(self.fname)
        extracted = {
                key: getattr(self, key) for key in self.keys
                }
        extracted.update(self.wcs_solution())

        return extracted

    def __getattr__(self, name):
        return self.header[name]


    def wcs_solution(self):
        file_wcs = wcs.WCS(self.header)
        coordinates = file_wcs.all_pix2world([1024, ], [1024, ], 1)
        solved_ra = coordinates[0][0]
        solved_dec = coordinates[1][0]

        return {'solved_ra': solved_ra, 'solved_dec': solved_dec}

def main(args):
    with open(args.output, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=Extracted.all_keys)
        writer.writeheader()

        with open(args.filelist) as infile:
            for line in infile:
                fname = line.strip('\n')
                Extracted(fname).writerow(writer)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filelist')
    parser.add_argument('-o', '--output', help='Output image',
            required=True, type=str)
    main(parser.parse_args())
