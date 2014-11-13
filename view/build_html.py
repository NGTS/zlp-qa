#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import argparse
from jinja2 import Template
from qa_common import get_logger

logger = get_logger(__file__)

class Image(object):
    def __init__(self, fname):
        self.fname = fname

    @property
    def stub(self):
        return os.path.basename(self.fname)

    @property
    def title(self):
        return (' '.join(os.path.splitext(self.stub)[0]
                .replace('_', ' ')
                .replace('-', ' ')
                .split()[1:])
                .capitalize())

    def __str__(self):
        return '<Image "{}">'.format(self.stub)

class Document(object):
    def __init__(self):
        self.images = []
        self.template = Template(open("templates/index.html").read())

    def add_image(self, i):
        self.images.append({
            'title': i.title,
            'location': i.fname,
            })

    def render(self, width=800):
        result = self.template.render(images=self.images,
                                      width='{}px'.format(width))
        return(result)
        
def main(args):
    files = sorted(glob.glob('{}/plots/*.{}'.format(args.sourcedir, args.extension)))
    files = [os.path.relpath(fname, args.sourcedir) for fname in files]
    logger.debug('Building html file from %s images', files)
    d = Document()

    for filename in files:
        logger.debug('Adding image %s', filename)
        d.add_image(Image(filename))

    logger.info('Rendering html file to %s', args.output)
    with open(args.output, 'w') as outfile:
        outfile.write(d.render())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sourcedir')
    parser.add_argument('-o', '--output', help='Output', required=True,
            type=str)
    parser.add_argument('--extension', help='File extension to use',
            required=True, type=str)
    main(parser.parse_args())
