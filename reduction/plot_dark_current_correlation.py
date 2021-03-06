#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import sys
import os

from qa_common import get_logger
from qa_common.plotting import plt
import qa_common

logger = get_logger(__file__)

def main(args):
    data = qa_common.CSVContainer(args.extracted)
    logger.info('Data read from %s', args.extracted)

    offset_value = 0.1
    offset = np.random.uniform(-offset_value, offset_value, data.chstemp.size)
    
    fig, axis = plt.subplots()

    axis.plot(data.chstemp + offset, data.dark, 'k.')
    axis.grid(True)
    axis.set_xlabel(r'Chassis temperature / C')
    axis.set_ylabel(r'Dark current / $\mathrm{e}^- s^{-1}$')
    
    fig.tight_layout()

    if args.output is not None:
        logger.info('Rendering file to %s', args.output)
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=False, type=argparse.FileType(mode='w'))
    parser.add_argument('extracted', type=argparse.FileType(mode='r'),
            help='List of files')
    main(parser.parse_args())

