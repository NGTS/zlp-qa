#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import fitsio

class Extracted(object):
    keys = ['fname', 'mjd', 'cmd_ra', 'cmd_dec',
            'tel_ra', 'tel_dec', 'crval1', 'crval2', 'cd1_1', 'cd1_2',
            'cd2_1', 'cd2_2', 'pv2_1', 'pv2_3', 'pv2_5',
            'skylevel', 'skynoise', 'numbrms', 'stdcrms']

    def __init__(self, fname):
        self.fname = fname

    def writerow(self, writer):
        writer.writerow(self.extract_data())

    def extract_data(self):
        self.header = fitsio.read_header(self.fname)
        return {
                key: getattr(self, key) for key in self.keys
                }

    def __getattr__(self, name):
        return self.header[name]


def main(args):
    with open(args.output, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=Extracted.keys)
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
