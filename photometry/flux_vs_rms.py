#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse

def main(args):
    print(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    parser.add_argument('--pre-sysrem', help='Input filename',
            type=str)
    parser.add_argument('--post-sysrem', help='Input filename',
            type=str)

    main(parser.parse_args())
