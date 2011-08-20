# coding: utf8

#  WeasyPrint converts web documents (HTML, CSS, ...) to PDF.
#  Copyright (C) 2011  Simon Sapin
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os.path

import png
from attest import Tests, assert_hook

from . import resource_filename
from ..document import PNGDocument
from . import make_expected_results


make_expected_results.make_all()


suite = Tests()


def make_filename(dirname, basename):
    return os.path.join(os.path.dirname(__file__), dirname, basename + '.png')


def format_pixel(lines, x, y):
    pixel = lines[y][3 * x:3 * (x + 1)]
    return ('#' + 3 * '%02x') % tuple(pixel)


def test_pixels(name, expected_width, expected_height, html):
    reader = png.Reader(filename=make_filename('expected_results', name))
    width, height, expected_lines, meta = reader.read()
    assert width == expected_width
    assert height == height
    assert meta['greyscale'] == False
    assert meta['alpha'] == False
    assert meta['bitdepth'] == 8
    expected_lines = list(expected_lines)

    document = PNGDocument.from_string(html)
    # Dummy filename, but in the right directory.
    document.base_url = resource_filename('<test>')
    filename = make_filename('test_results', name)
    document.write_to(filename)


    reader = png.Reader(filename=filename)
    width, height, lines, meta = reader.read()
    lines = list(lines)

    assert width == expected_width
    assert height == height
    assert meta['greyscale'] == False
    assert meta['alpha'] == False
    assert meta['bitdepth'] == 8
    assert len(lines) == height
    assert len(lines[0]) == width * 3
    if lines != expected_lines:
        for y in xrange(height):
            for x in xrange(width):
                pixel = format_pixel(lines, x, y)
                expected_pixel = format_pixel(expected_lines, x, y)
                assert pixel == expected_pixel, \
                    'Pixel (%i, %i) does not match in %s' % (x, y, name)

@suite.test
def test_canvas_background():
    test_pixels('all_blue', 10, 10, '''
        <style>
            @page { size: 10px }
            /* body’s background propagates to the whole canvas */
            body { margin: 2px; background: #00f; height: 5px }
        </style>
        <body>
    ''')
    test_pixels('blocks', 10, 10, '''
        <style>
            @page { size: 10px }
            /* html’s background propagates to the whole canvas */
            html { margin: 1px; background: #f00 }
            /* html has a background, so body’s does not propagate */
            body { margin: 1px; background: #00f; height: 5px }
        </style>
        <body>
    ''')


@suite.test
def test_background_image():
    for name, css in [
        ('repeat', ''),
        ('repeat_x', 'repeat-x'),
        ('repeat_y', 'repeat-y'),

        ('left_top', 'no-repeat 0 0%'),
        ('center_top', 'no-repeat 50% 0px'),
        ('right_top', 'no-repeat 6px top'),

        ('left_center', 'no-repeat left center'),
        ('center_center', 'no-repeat 3px 3px'),
        ('right_center', 'no-repeat 100% 50%'),

        ('left_bottom', 'no-repeat 0% bottom'),
        ('center_bottom', 'no-repeat center 6px'),
        ('right_bottom', 'no-repeat 6px 100%'),

        ('repeat_x_1px_2px', 'repeat-x 1px 2px'),
        ('repeat_y_2px_1px', 'repeat-y 2px 1px'),

        ('fixed', 'no-repeat fixed'),
        ('fixed_right', 'no-repeat fixed right 3px'),
    ]:
        test_pixels('background_' + name, 14, 16, '''
            <style>
                @page { size: 14px 16px }
                html { background: #fff }
                body { margin: 2px; height: 10px;
                       background: url(pattern.png) %s }
            </style>
            <body>
        ''' % (css,))


@suite.test
def test_list_style_image():
    for position in ('inside', 'outside'):
        test_pixels('list_style_image_' + position, 12, 10, '''
            <style>
                @page { size: 12px 10px }
                body { margin: 0; background: white }
                ul { margin: 2px 2px 2px 7px; list-style: url(pattern.png) %s;
                     font-size: 4px; }
            </style>
            <ul><li>
        ''' % (position,))
