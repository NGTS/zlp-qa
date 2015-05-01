#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import argparse
from jinja2 import Template
from qa_common import get_logger
from collections import defaultdict

logger = get_logger(__file__)

help_lookup = {
        'overscan-levels': 'overscan-levels.html',
        'dark-levels': 'dark-levels.html',
        'dark-correlation': 'dark-correlation.html',
        'mbias': 'masters.html',
        'mbias-smoothed': 'masters.html',
        'mdark': 'masters.html',
        'mdark-smoothed': 'masters.html',
        'mflat': 'masters.html',
        'mflat-smoothed': 'masters.html',
        'total-flat-adu': 'total-flat-adu.html',
        'flux-vs-rms': 'flux-vs-rms.html',
        'rms-vs-time': 'rms-vs-time.html',
        'rms-with-binning': 'rms-with-binning.html',
        'photometry-time-series': 'photometry-time-series.html',
        'binned-lightcurves-by-brightness': 'binned-lightcurves-by-brightness.html',
        'extracted-astrometric-parameters': 'extracted-astrometric-parameters.html',
        'pixel-centre-of-mass': 'pixel-centre-of-mass.html',
        'pixel-centre-of-mass': 'pixel-centre-of-mass.html',
        'vector-astrometry': 'astrometry-rms.html',
        'psf': 'psf.html',
        }

for i in range(10):
    name = 'vector-astrometry-{:02d}'.format(i)
    help_lookup[name] = 'astrometry-rms.html'

    name = 'psf-{:02d}'.format(i)
    help_lookup[name] = 'psf.html'

class Image(object):

    counter = defaultdict(int)

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

    @property
    def anchor(self):
        _anchor = self.title.lower().replace(' ', '-')
        increment = self.counter.get(_anchor, 0)
        self.counter[_anchor] += 1
        if increment:
            return _anchor + '-{:02d}'.format(increment)
        else:
            return _anchor

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
            'anchor': i.anchor,
            })

    def render(self, width=800):
        result = self.template.render(images=self.images,
                help_lookup=help_lookup,
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
