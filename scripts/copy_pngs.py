#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import shutil

def copy_file(i, fname, outputdir, stub):
    output_filename = os.path.join(outputdir, '{:02d}-{}.png'.format(i, stub))
    if not os.path.isfile(output_filename):
        shutil.copyfile(fname, output_filename)

def main(args):
    with open(args.filelist) as infile:
        files = [line.strip() for line in infile]

    nfiles = len(files)
    for i, file_index in enumerate(xrange(0, nfiles, nfiles / args.nfiles)):
        copy_file(args.offset + i, files[file_index], args.outputdir, args.stub)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filelist')
    parser.add_argument('-o', '--outputdir', required=True)
    parser.add_argument('--stub', required=True)
    parser.add_argument('--nfiles', type=int, default=5, required=False)
    parser.add_argument('--offset', type=int, required=True)
    main(parser.parse_args())