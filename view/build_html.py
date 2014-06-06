#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import argparse

class Image(object):
    def __init__(self, fname):
        self.fname = fname

    @property
    def stub(self):
        return os.path.basename(self.fname)

    def html(self, width=None, height=None):
        return '<img src="{fname}" width="{width}" height="{height}" />'.format(
                fname=self.fname,
                width=width if width else '',
                height=height if height else '')

    @property
    def title(self):
        return (os.path.splitext(self.stub)[0]
                .replace('_', ' ')
                .replace('-', ' ')
                .capitalize())

    def __str__(self):
        return '<Image "{}">'.format(self.stub)

class Document(object):
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.outline = '''<html>
<head>
</head>
<body>
    <div id='images'>
    {}
    </div>
</body>
</html>'''
        self.images = []

    def add_image(self, i):
        self.images.append({
            'title': i.title,
            'tag': i.html(width=self.width, height=self.height),
            })

    def render(self, level=5):
        h_level = 'h{}'.format(level)
        out = []
        for image in self.images:
            out.append('''<{hlevel}>{title}</h5>{imgsrc}'''.format(
                hlevel=h_level,
                title=image['title'],
                imgsrc=image['tag'],))
        return self.outline.format('<br />'.join(out))

def main(args):
    files = glob.glob('plots/*.png')
    d = Document(width=640, height=480)

    for filename in files:
        d.add_image(Image(filename))


    with open(args.output, 'w') as outfile:
        outfile.write(d.render(level=3))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output', required=True,
            type=str)
    main(parser.parse_args())
