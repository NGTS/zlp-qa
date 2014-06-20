#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import argparse
import numpy as np
import sys

from plot_overscan_levels import compute_limits

def main(args):
    data = pd.read_table(args.extracted, sep=',')

    offset_value = 0.1
    offset = np.random.uniform(-offset_value, offset_value, data.chstemp.size)
    
    fig, axis = plt.subplots(figsize=(11, 8))

    axis.plot(data.chstemp + offset, data.dark, 'k.')
    axis.set_ylim(1, 7)
    axis.grid(True)
    axis.set_xlabel(r'Chassis temperature / C')
    axis.set_ylabel(r'Dark current / $\mathrm{e}^- s^{-1}$')
    
    fig.tight_layout()
    if args.output.strip() == '-':
        fig.savefig(sys.stdout, bbox_inches='tight')
    else:
        fig.savefig(args.output, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=True, type=str)
    parser.add_argument('extracted', type=str, help='List of files')
    main(parser.parse_args())

