#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from fetch_2mass import Stilts

def match(input_catalogue, reference_catalogue, output_filename, error=10):
    in1 = '{}#1'.format(input_catalogue)
    in2 = '{}#1'.format(reference_catalogue)

    ra1 = 'radiansToDegrees(RA)'
    dec1 = 'radiansToDegrees(DEC)'

    ra2 = 'ra_1'
    dec2 = 'dec_1'

    Stilts.run('tskymatch2', in1=in1, in2=in2, out=output_filename,
            error=error, ra1=ra1, dec1=dec1, ra2=ra2, dec2=dec2)


def main(args):
    match(args.catalogue, getattr(args, '2mass'), args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalogue', help='Input catalogue')
    parser.add_argument('--2mass', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())

