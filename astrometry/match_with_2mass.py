#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess as sp
import logging
logging.basicConfig(level=logging.INFO)
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


def match(input_catalogue, reference_catalogue, output_filename, error=10):
    in1 = '{}#1'.format(input_catalogue)
    in2 = '{}'.format(reference_catalogue)

    ra1 = 'radiansToDegrees(RA)'
    dec1 = 'radiansToDegrees(DEC)'

    ra2 = 'ra'
    dec2 = 'dec'

    Stilts.run('tskymatch2', in1=in1, in2=in2,
            out=output_filename,
            ifmt2='csv',
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

