"""
pygooglechart - A complete Python wrapper for the Google Chart API

http://pygooglechart.slowchop.com/

Copyright 2007-2008 Gerald Kaszuba

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os
import urllib
import urllib2
import math
import random
import re
import warnings
import copy

# Helper variables and functions
# -----------------------------------------------------------------------------

__version__ = '0.2.1'
__author__ = 'Gerald Kaszuba'

reo_colour = re.compile('^([A-Fa-f0-9]{2,2}){3,4}$')

def _check_colour(colour):
    if not reo_colour.match(colour):
        raise InvalidParametersException('Colours need to be in ' \
            'RRGGBB or RRGGBBAA format. One of your colours has %s' % \
            colour)


def _reset_warnings():
    """Helper function to reset all warnings. Used by the unit tests."""
    globals()['__warningregistry__'] = None


# Exception Classes
# -----------------------------------------------------------------------------


class PyGoogleChartException(Exception):
    pass


class DataOutOfRangeException(PyGoogleChartException):
    pass


class UnknownDataTypeException(PyGoogleChartException):
    pass


class NoDataGivenException(PyGoogleChartException):
    pass


class InvalidParametersException(PyGoogleChartException):
    pass


class BadContentTypeException(PyGoogleChartException):
    pass


class AbstractClassException(PyGoogleChartException):
    pass


class UnknownChartType(PyGoogleChartException):
    pass


# Data Classes
# -----------------------------------------------------------------------------


class Data(object):

    def __init__(self, data):
        if type(self) == Data:
            raise AbstractClassException('This is an abstract class')
        self.data = data

    @classmethod
    def float_scale_value(cls, value, range):
        lower, upper = range
        assert(upper > lower)
        scaled = (value - lower) * (float(cls.max_value) / (upper - lower))
        return scaled

    @classmethod
    def clip_value(cls, value):
        return max(0, min(value, cls.max_value))

    @classmethod
    def int_scale_value(cls, value, range):
        return int(round(cls.float_scale_value(value, range)))

    @classmethod
    def scale_value(cls, value, range):
        scaled = cls.int_scale_value(value, range)
        clipped = cls.clip_value(scaled)
        Data.check_clip(scaled, clipped)
        return clipped

    @staticmethod
    def check_clip(scaled, clipped):
        if clipped != scaled:
            warnings.warn('One or more of of your data points has been '
                'clipped because it is out of range.')


class SimpleData(Data):

    max_value = 61
    enc_map = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    def __repr__(self):
        encoded_data = []
        for data in self.data:
            sub_data = []
            for value in data:
                if value is None:
                    sub_data.append('_')
                elif value >= 0 and value <= self.max_value:
                    sub_data.append(SimpleData.enc_map[value])
                else:
                    raise DataOutOfRangeException('cannot encode value: %d'
                                                  % value)
            encoded_data.append(''.join(sub_data))
        return 'chd=s:' + ','.join(encoded_data)


class TextData(Data):

    max_value = 100

    def __repr__(self):
        encoded_data = []
        for data in self.data:
            sub_data = []
            for value in data:
                if value is None:
                    sub_data.append(-1)
                elif value >= 0 and value <= self.max_value:
                    sub_data.append("%.1f" % float(value))
                else:
                    raise DataOutOfRangeException()
            encoded_data.append(','.join(sub_data))
        return 'chd=t:' + '|'.join(encoded_data)

    @classmethod
    def scale_value(cls, value, range):
        # use float values instead of integers because we don't need an encode
        # map index
        scaled = cls.float_scale_value(value, range)
        clipped = cls.clip_value(scaled)
        Data.check_clip(scaled, clipped)
        return clipped


class ExtendedData(Data):

    max_value = 4095
    enc_map = \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.'

    def __repr__(self):
        encoded_data = []
        enc_size = len(ExtendedData.enc_map)
        for data in self.data:
            sub_data = []
            for value in data:
                if value is None:
                    sub_data.append('__')
                elif value >= 0 and value <= self.max_value:
                    first, second = divmod(int(value), enc_size)
                    sub_data.append('%s%s' % (
                        ExtendedData.enc_map[first],
                        ExtendedData.enc_map[second]))
                else:
                    raise DataOutOfRangeException( \
                        'Item #%i "%s" is out of range' % (data.index(value), \
                        value))
            encoded_data.append(''.join(sub_data))
        return 'chd=e:' + ','.join(encoded_data)


# Axis Classes
# -----------------------------------------------------------------------------


class Axis(object):

    BOTTOM = 'x'
    TOP = 't'
    LEFT = 'y'
    RIGHT = 'r'
    TYPES = (BOTTOM, TOP, LEFT, RIGHT)

    def __init__(self, axis_index, axis_type, **kw):
        assert(axis_type in Axis.TYPES)
        self.has_style = False
        self.axis_index = axis_index
        self.axis_type = axis_type
        self.positions = None

    def set_index(self, axis_index):
        self.axis_index = axis_index

    def set_positions(self, positions):
        self.positions = positions

    def set_style(self, colour, font_size=None, alignment=None):
        _check_colour(colour)
        self.colour = colour
        self.font_size = font_size
        self.alignment = alignment
        self.has_style = True

    def style_to_url(self):
        bits = []
        bits.append(str(self.axis_index))
        bits.append(self.colour)
        if self.font_size is not None:
            bits.append(str(self.font_size))
            if self.alignment is not None:
                bits.append(str(self.alignment))
        return ','.join(bits)

    def positions_to_url(self):
        bits = []
        bits.append(str(self.axis_index))
        bits += [str(a) for a in self.positions]
        return ','.join(bits)


class LabelAxis(Axis):

    def __init__(self, axis_index, axis_type, values, **kwargs):
        Axis.__init__(self, axis_index, axis_type, **kwargs)
        self.values = [str(a) for a in values]

    def __repr__(self):
        return '%i:|%s' % (self.axis_index, '|'.join(self.values))


class RangeAxis(Axis):

    def __init__(self, axis_index, axis_type, low, high, **kwargs):
        Axis.__init__(self, axis_index, axis_type, **kwargs)
        self.low = low
        self.high = high

    def __repr__(self):
        return '%i,%s,%s' % (self.axis_index, self.low, self.high)

# Chart Classes
# -----------------------------------------------------------------------------


class Chart(object):
    """Abstract class for all chart types.

    width are height specify the dimensions of the image. title sets the title
    of the chart. legend requires a list that corresponds to datasets.
    """

    BASE_URL = 'http://chart.apis.google.com/chart?'
    BACKGROUND = 'bg'
    CHART = 'c'
    ALPHA = 'a'
    VALID_SOLID_FILL_TYPES = (BACKGROUND, CHART, ALPHA)
    SOLID = 's'
    LINEAR_GRADIENT = 'lg'
    LINEAR_STRIPES = 'ls'

    def __init__(self, width, height, title=None, legend=None, colours=None,
            auto_scale=True, x_range=None, y_range=None,
            colours_within_series=None):
        if type(self) == Chart:
            raise AbstractClassException('This is an abstract class')
        assert(isinstance(width, int))
        assert(isinstance(height, int))
        self.width = width
        self.height = height
        self.data = []
        self.set_title(title)
        self.set_legend(legend)
        self.set_legend_position(None)
        self.set_colours(colours)
        self.set_colours_within_series(colours_within_series)

        # Data for scaling.
        self.auto_scale = auto_scale  # Whether to automatically scale data
        self.x_range = x_range  # (min, max) x-axis range for scaling
        self.y_range = y_range  # (min, max) y-axis range for scaling
        self.scaled_data_class = None
        self.scaled_x_range = None
        self.scaled_y_range = None

        self.fill_types = {
            Chart.BACKGROUND: None,
            Chart.CHART: None,
            Chart.ALPHA: None,
        }
        self.fill_area = {
            Chart.BACKGROUND: None,
            Chart.CHART: None,
            Chart.ALPHA: None,
        }
        self.axis = []
        self.markers = []
        self.line_styles = {}
        self.grid = None

    # URL generation
    # -------------------------------------------------------------------------

    def get_url(self, data_class=None):
        url_bits = self.get_url_bits(data_class=data_class)
        return self.BASE_URL + '&'.join(url_bits)

    def get_url_bits(self, data_class=None):
        url_bits = []
        # required arguments
        url_bits.append(self.type_to_url())
        url_bits.append('chs=%ix%i' % (self.width, self.height))
        url_bits.append(self.data_to_url(data_class=data_class))
        # optional arguments
        if self.title:
            url_bits.append('chtt=%s' % self.title)
        if self.legend:
            url_bits.append('chdl=%s' % '|'.join(self.legend))
        if self.legend_position:
            url_bits.append('chdlp=%s' % (self.legend_position))
        if self.colours:
            url_bits.append('chco=%s' % ','.join(self.colours))            
        if self.colours_within_series:
            url_bits.append('chco=%s' % '|'.join(self.colours_within_series))
        ret = self.fill_to_url()
        if ret:
            url_bits.append(ret)
        ret = self.axis_to_url()
        if ret:
            url_bits.append(ret)                    
        if self.markers:
            url_bits.append(self.markers_to_url())        
        if self.line_styles:
            style = []
            for index in xrange(max(self.line_styles) + 1):
                if index in self.line_styles:
                    values = self.line_styles[index]
                else:
                    values = ('1', )
                style.append(','.join(values))
            url_bits.append('chls=%s' % '|'.join(style))
        if self.grid:
            url_bits.append('chg=%s' % self.grid)
        return url_bits

    # Downloading
    # -------------------------------------------------------------------------

    def download(self, file_name):
        opener = urllib2.urlopen(self.get_url())

        if opener.headers['content-type'] != 'image/png':
            raise BadContentTypeException('Server responded with a ' \
                'content-type of %s' % opener.headers['content-type'])

        open(file_name, 'wb').write(opener.read())

    # Simple settings
    # -------------------------------------------------------------------------

    def set_title(self, title):
        if title:
            self.title = urllib.quote(title)
        else:
            self.title = None

    def set_legend(self, legend):
        """legend needs to be a list, tuple or None"""
        assert(isinstance(legend, list) or isinstance(legend, tuple) or
            legend is None)
        if legend:
            self.legend = [urllib.quote(a) for a in legend]
        else:
            self.legend = None

    def set_legend_position(self, legend_position):
        if legend_position:
            self.legend_position = urllib.quote(legend_position)
        else:    
            self.legend_position = None

    # Chart colours
    # -------------------------------------------------------------------------

    def set_colours(self, colours):
        # colours needs to be a list, tuple or None
        assert(isinstance(colours, list) or isinstance(colours, tuple) or
            colours is None)
        # make sure the colours are in the right format
        if colours:
            for col in colours:
                _check_colour(col)
        self.colours = colours

    def set_colours_within_series(self, colours):
        # colours needs to be a list, tuple or None
        assert(isinstance(colours, list) or isinstance(colours, tuple) or
            colours is None)
        # make sure the colours are in the right format
        if colours:
            for col in colours:
                _check_colour(col)
        self.colours_within_series = colours        

    # Background/Chart colours
    # -------------------------------------------------------------------------

    def fill_solid(self, area, colour):
        assert(area in Chart.VALID_SOLID_FILL_TYPES)
        _check_colour(colour)
        self.fill_area[area] = colour
        self.fill_types[area] = Chart.SOLID

    def _check_fill_linear(self, angle, *args):
        assert(isinstance(args, list) or isinstance(args, tuple))
        assert(angle >= 0 and angle <= 90)
        assert(len(args) % 2 == 0)
        args = list(args)  # args is probably a tuple and we need to mutate
        for a in xrange(len(args) / 2):
            col = args[a * 2]
            offset = args[a * 2 + 1]
            _check_colour(col)
            assert(offset >= 0 and offset <= 1)
            args[a * 2 + 1] = str(args[a * 2 + 1])
        return args

    def fill_linear_gradient(self, area, angle, *args):
        assert(area in Chart.VALID_SOLID_FILL_TYPES)
        args = self._check_fill_linear(angle, *args)
        self.fill_types[area] = Chart.LINEAR_GRADIENT
        self.fill_area[area] = ','.join([str(angle)] + args)

    def fill_linear_stripes(self, area, angle, *args):
        assert(area in Chart.VALID_SOLID_FILL_TYPES)
        args = self._check_fill_linear(angle, *args)
        self.fill_types[area] = Chart.LINEAR_STRIPES
        self.fill_area[area] = ','.join([str(angle)] + args)

    def fill_to_url(self):
        areas = []
        for area in (Chart.BACKGROUND, Chart.CHART, Chart.ALPHA):
            if self.fill_types[area]:
                areas.append('%s,%s,%s' % (area, self.fill_types[area], \
                    self.fill_area[area]))
        if areas:
            return 'chf=' + '|'.join(areas)

    # Data
    # -------------------------------------------------------------------------

    def data_class_detection(self, data):
        """Determines the appropriate data encoding type to give satisfactory
        resolution (http://code.google.com/apis/chart/#chart_data).
        """
        assert(isinstance(data, list) or isinstance(data, tuple))
        if not isinstance(self, (LineChart, BarChart, ScatterChart)):
            # From the link above:
            #   Simple encoding is suitable for all other types of chart
            #   regardless of size.
            return SimpleData
        elif self.height < 100:
            # The link above indicates that line and bar charts less
            # than 300px in size can be suitably represented with the
            # simple encoding. I've found that this isn't sufficient,
            # e.g. examples/line-xy-circle.png. Let's try 100px.
            return SimpleData
        else:
            return ExtendedData

    def _filter_none(self, data):
        return [r for r in data if r is not None]

    def data_x_range(self):
        """Return a 2-tuple giving the minimum and maximum x-axis
        data range.
        """
        try:
            lower = min([min(self._filter_none(s))
                         for type, s in self.annotated_data()
                         if type == 'x'])
            upper = max([max(self._filter_none(s))
                         for type, s in self.annotated_data()
                         if type == 'x'])
            return (lower, upper)
        except ValueError:
            return None     # no x-axis datasets

    def data_y_range(self):
        """Return a 2-tuple giving the minimum and maximum y-axis
        data range.
        """
        try:
            lower = min([min(self._filter_none(s))
                         for type, s in self.annotated_data()
                         if type == 'y'])
            upper = max([max(self._filter_none(s)) + 1
                         for type, s in self.annotated_data()
                         if type == 'y'])
            return (lower, upper)
        except ValueError:
            return None     # no y-axis datasets

    def scaled_data(self, data_class, x_range=None, y_range=None):
        """Scale `self.data` as appropriate for the given data encoding
        (data_class) and return it.

        An optional `y_range` -- a 2-tuple (lower, upper) -- can be
        given to specify the y-axis bounds. If not given, the range is
        inferred from the data: (0, <max-value>) presuming no negative
        values, or (<min-value>, <max-value>) if there are negative
        values.  `self.scaled_y_range` is set to the actual lower and
        upper scaling range.

        Ditto for `x_range`. Note that some chart types don't have x-axis
        data.
        """
        self.scaled_data_class = data_class

        # Determine the x-axis range for scaling.
        if x_range is None:
            x_range = self.data_x_range()
            if x_range and x_range[0] > 0:
                x_range = (x_range[0], x_range[1])
        self.scaled_x_range = x_range

        # Determine the y-axis range for scaling.
        if y_range is None:
            y_range = self.data_y_range()
            if y_range and y_range[0] > 0:
                y_range = (y_range[0], y_range[1])
        self.scaled_y_range = y_range

        scaled_data = []
        for type, dataset in self.annotated_data():
            if type == 'x':
                scale_range = x_range
            elif type == 'y':
                scale_range = y_range
            elif type == 'marker-size':
                scale_range = (0, max(dataset))
            scaled_dataset = []
            for v in dataset:
                if v is None:
                    scaled_dataset.append(None)
                else:
                    scaled_dataset.append(
                        data_class.scale_value(v, scale_range))
            scaled_data.append(scaled_dataset)
        return scaled_data

    def add_data(self, data):
        self.data.append(data)
        return len(self.data) - 1  # return the "index" of the data set

    def data_to_url(self, data_class=None):
        if not data_class:
            data_class = self.data_class_detection(self.data)
        if not issubclass(data_class, Data):
            raise UnknownDataTypeException()
        if self.auto_scale:
            data = self.scaled_data(data_class, self.x_range, self.y_range)
        else:
            data = self.data
        return repr(data_class(data))

    def annotated_data(self):
        for dataset in self.data:
            yield ('x', dataset)

    # Axis Labels
    # -------------------------------------------------------------------------

    def set_axis_labels(self, axis_type, values):
        assert(axis_type in Axis.TYPES)
        values = [urllib.quote(str(a)) for a in values]
        axis_index = len(self.axis)
        axis = LabelAxis(axis_index, axis_type, values)
        self.axis.append(axis)
        return axis_index

    def set_axis_range(self, axis_type, low, high):
        assert(axis_type in Axis.TYPES)
        axis_index = len(self.axis)
        axis = RangeAxis(axis_index, axis_type, low, high)
        self.axis.append(axis)
        return axis_index

    def set_axis_positions(self, axis_index, positions):
        try:
            self.axis[axis_index].set_positions(positions)
        except IndexError:
            raise InvalidParametersException('Axis index %i has not been ' \
                'created' % axis)

    def set_axis_style(self, axis_index, colour, font_size=None, \
            alignment=None):
        try:
            self.axis[axis_index].set_style(colour, font_size, alignment)
        except IndexError:
            raise InvalidParametersException('Axis index %i has not been ' \
                'created' % axis)

    def axis_to_url(self):
        available_axis = []
        label_axis = []
        range_axis = []
        positions = []
        styles = []
        index = -1
        for axis in self.axis:
            available_axis.append(axis.axis_type)
            if isinstance(axis, RangeAxis):
                range_axis.append(repr(axis))
            if isinstance(axis, LabelAxis):
                label_axis.append(repr(axis))
            if axis.positions:
                positions.append(axis.positions_to_url())
            if axis.has_style:
                styles.append(axis.style_to_url())
        if not available_axis:
            return
        url_bits = []
        url_bits.append('chxt=%s' % ','.join(available_axis))
        if label_axis:
            url_bits.append('chxl=%s' % '|'.join(label_axis))
        if range_axis:
            url_bits.append('chxr=%s' % '|'.join(range_axis))
        if positions:
            url_bits.append('chxp=%s' % '|'.join(positions))
        if styles:
            url_bits.append('chxs=%s' % '|'.join(styles))
        return '&'.join(url_bits)

    # Markers, Ranges and Fill area (chm)
    # -------------------------------------------------------------------------

    def markers_to_url(self):        
        return 'chm=%s' % '|'.join([','.join(a) for a in self.markers])

    def add_marker(self, index, point, marker_type, colour, size, priority=0):
        self.markers.append((marker_type, colour, str(index), str(point), \
            str(size), str(priority)))

    def add_horizontal_range(self, colour, start, stop):
        self.markers.append(('r', colour, '0', str(start), str(stop)))

    def add_data_line(self, colour, data_set, size, priority=0):
        self.markers.append(('D', colour, str(data_set), '0', str(size), str(priority)))

    def add_marker_text(self, string, colour, data_set, data_point, size, priority=0):
        self.markers.append((str(string), colour, str(data_set), str(data_point), str(size), str(priority)))        

    def add_vertical_range(self, colour, start, stop):
        self.markers.append(('R', colour, '0', str(start), str(stop)))

    def add_fill_range(self, colour, index_start, index_end):
        self.markers.append(('b', colour, str(index_start), str(index_end), \
            '1'))

    def add_fill_simple(self, colour):
        self.markers.append(('B', colour, '1', '1', '1'))

    # Line styles
    # -------------------------------------------------------------------------

    def set_line_style(self, index, thickness=1, line_segment=None, \
            blank_segment=None):
        value = []
        value.append(str(thickness))
        if line_segment:
            value.append(str(line_segment))
            value.append(str(blank_segment))
        self.line_styles[index] = value

    # Grid
    # -------------------------------------------------------------------------

    def set_grid(self, x_step, y_step, line_segment=1, \
            blank_segment=0):
        self.grid = '%s,%s,%s,%s' % (x_step, y_step, line_segment, \
            blank_segment)


class ScatterChart(Chart):

    def type_to_url(self):
        return 'cht=s'

    def annotated_data(self):
        yield ('x', self.data[0])
        yield ('y', self.data[1])
        if len(self.data) > 2:
            # The optional third dataset is relative sizing for point
            # markers.
            yield ('marker-size', self.data[2])


class LineChart(Chart):

    def __init__(self, *args, **kwargs):
        if type(self) == LineChart:
            raise AbstractClassException('This is an abstract class')
        Chart.__init__(self, *args, **kwargs)


class SimpleLineChart(LineChart):

    def type_to_url(self):
        return 'cht=lc'

    def annotated_data(self):
        # All datasets are y-axis data.
        for dataset in self.data:
            yield ('y', dataset)


class SparkLineChart(SimpleLineChart):

    def type_to_url(self):
        return 'cht=ls'


class XYLineChart(LineChart):

    def type_to_url(self):
        return 'cht=lxy'

    def annotated_data(self):
        # Datasets alternate between x-axis, y-axis.
        for i, dataset in enumerate(self.data):
            if i % 2 == 0:
                yield ('x', dataset)
            else:
                yield ('y', dataset)


class BarChart(Chart):

    def __init__(self, *args, **kwargs):
        if type(self) == BarChart:
            raise AbstractClassException('This is an abstract class')
        Chart.__init__(self, *args, **kwargs)
        self.bar_width = None
        self.zero_lines = {}

    def set_bar_width(self, bar_width):
        self.bar_width = bar_width

    def set_zero_line(self, index, zero_line):
        self.zero_lines[index] = zero_line

    def get_url_bits(self, data_class=None, skip_chbh=False):
        url_bits = Chart.get_url_bits(self, data_class=data_class)
        if not skip_chbh and self.bar_width is not None:
            url_bits.append('chbh=%i' % self.bar_width)
        zero_line = []
        if self.zero_lines:
            for index in xrange(max(self.zero_lines) + 1):
                if index in self.zero_lines:
                    zero_line.append(str(self.zero_lines[index]))
                else:
                    zero_line.append('0')
            url_bits.append('chp=%s' % ','.join(zero_line))
        return url_bits


class StackedHorizontalBarChart(BarChart):

    def type_to_url(self):
        return 'cht=bhs'


class StackedVerticalBarChart(BarChart):

    def type_to_url(self):
        return 'cht=bvs'

    def annotated_data(self):
        for dataset in self.data:
            yield ('y', dataset)


class GroupedBarChart(BarChart):

    def __init__(self, *args, **kwargs):
        if type(self) == GroupedBarChart:
            raise AbstractClassException('This is an abstract class')
        BarChart.__init__(self, *args, **kwargs)
        self.bar_spacing = None
        self.group_spacing = None

    def set_bar_spacing(self, spacing):
        """Set spacing between bars in a group."""
        self.bar_spacing = spacing

    def set_group_spacing(self, spacing):
        """Set spacing between groups of bars."""
        self.group_spacing = spacing

    def get_url_bits(self, data_class=None):
        # Skip 'BarChart.get_url_bits' and call Chart directly so the parent
        # doesn't add "chbh" before we do.
        url_bits = BarChart.get_url_bits(self, data_class=data_class,
            skip_chbh=True)
        if self.group_spacing is not None:
            if self.bar_spacing is None:
                raise InvalidParametersException('Bar spacing is required ' \
                    'to be set when setting group spacing')
            if self.bar_width is None:
                raise InvalidParametersException('Bar width is required to ' \
                    'be set when setting bar spacing')
            url_bits.append('chbh=%i,%i,%i'
                % (self.bar_width, self.bar_spacing, self.group_spacing))
        elif self.bar_spacing is not None:
            if self.bar_width is None:
                raise InvalidParametersException('Bar width is required to ' \
                    'be set when setting bar spacing')
            url_bits.append('chbh=%i,%i' % (self.bar_width, self.bar_spacing))
        elif self.bar_width:
            url_bits.append('chbh=%i' % self.bar_width)
        return url_bits


class GroupedHorizontalBarChart(GroupedBarChart):

    def type_to_url(self):
        return 'cht=bhg'


class GroupedVerticalBarChart(GroupedBarChart):

    def type_to_url(self):
        return 'cht=bvg'

    def annotated_data(self):
        for dataset in self.data:
            yield ('y', dataset)


class PieChart(Chart):

    def __init__(self, *args, **kwargs):
        if type(self) == PieChart:
            raise AbstractClassException('This is an abstract class')
        Chart.__init__(self, *args, **kwargs)
        self.pie_labels = []
        if self.y_range:
            warnings.warn('y_range is not used with %s.' % \
                (self.__class__.__name__))

    def set_pie_labels(self, labels):
        self.pie_labels = [urllib.quote(a) for a in labels]

    def get_url_bits(self, data_class=None):
        url_bits = Chart.get_url_bits(self, data_class=data_class)
        if self.pie_labels:
            url_bits.append('chl=%s' % '|'.join(self.pie_labels))
        return url_bits

    def annotated_data(self):
        # Datasets are all y-axis data. However, there should only be
        # one dataset for pie charts.
        for dataset in self.data:
            yield ('x', dataset)

    def scaled_data(self, data_class, x_range=None, y_range=None):
        if not x_range:
            x_range = [0, sum(self.data[0])]
        return Chart.scaled_data(self, data_class, x_range, self.y_range)


class PieChart2D(PieChart):

    def type_to_url(self):
        return 'cht=p'


class PieChart3D(PieChart):

    def type_to_url(self):
        return 'cht=p3'


class VennChart(Chart):

    def type_to_url(self):
        return 'cht=v'

    def annotated_data(self):
        for dataset in self.data:
            yield ('y', dataset)


class RadarChart(Chart):

    def type_to_url(self):
        return 'cht=r'


class SplineRadarChart(RadarChart):

    def type_to_url(self):
        return 'cht=rs'


class MapChart(Chart):

    def __init__(self, *args, **kwargs):
        Chart.__init__(self, *args, **kwargs)
        self.geo_area = 'world'
        self.codes = []

    def type_to_url(self):
        return 'cht=t'

    def set_codes(self, codes):
        self.codes = codes

    def get_url_bits(self, data_class=None):
        url_bits = Chart.get_url_bits(self, data_class=data_class)
        url_bits.append('chtm=%s' % self.geo_area)
        if self.codes:
            url_bits.append('chld=%s' % ''.join(self.codes))
        return url_bits


class GoogleOMeterChart(PieChart):
    """Inheriting from PieChart because of similar labeling"""

    def __init__(self, *args, **kwargs):
        PieChart.__init__(self, *args, **kwargs)
        if self.auto_scale and not self.x_range:
            warnings.warn('Please specify an x_range with GoogleOMeterChart, '
                'otherwise one arrow will always be at the max.')

    def type_to_url(self):
        return 'cht=gom'


class QRChart(Chart):

    def __init__(self, *args, **kwargs):
        Chart.__init__(self, *args, **kwargs)
        self.encoding = None
        self.ec_level = None
        self.margin = None

    def type_to_url(self):
        return 'cht=qr'

    def data_to_url(self, data_class=None):
        if not self.data:
            raise NoDataGivenException()
        return 'chl=%s' % urllib.quote(self.data[0])

    def get_url_bits(self, data_class=None):
        url_bits = Chart.get_url_bits(self, data_class=data_class)
        if self.encoding:
            url_bits.append('choe=%s' % self.encoding)
        if self.ec_level:
            url_bits.append('chld=%s|%s' % (self.ec_level, self.margin))
        return url_bits

    def set_encoding(self, encoding):
        self.encoding = encoding

    def set_ec(self, level, margin):
        self.ec_level = level
        self.margin = margin


class ChartGrammar(object):

    def __init__(self):
        self.grammar = None
        self.chart = None

    def parse(self, grammar):
        self.grammar = grammar
        self.chart = self.create_chart_instance()

        for attr in self.grammar:
            if attr in ('w', 'h', 'type', 'auto_scale', 'x_range', 'y_range'):
                continue  # These are already parsed in create_chart_instance
            attr_func = 'parse_' + attr
            if not hasattr(self, attr_func):
                warnings.warn('No parser for grammar attribute "%s"' % (attr))
                continue
            getattr(self, attr_func)(grammar[attr])

        return self.chart

    def parse_data(self, data):
        self.chart.data = data

    @staticmethod
    def get_possible_chart_types():
        possible_charts = []
        for cls_name in globals().keys():
            if not cls_name.endswith('Chart'):
                continue
            cls = globals()[cls_name]
            # Check if it is an abstract class
            try:
                a = cls(1, 1, auto_scale=False)
                del a
            except AbstractClassException:
                continue
            # Strip off "Class"
            possible_charts.append(cls_name[:-5])
        return possible_charts

    def create_chart_instance(self, grammar=None):
        if not grammar:
            grammar = self.grammar
        assert(isinstance(grammar, dict))  # grammar must be a dict
        assert('w' in grammar)  # width is required
        assert('h' in grammar)  # height is required
        assert('type' in grammar)  # type is required
        chart_type = grammar['type']
        w = grammar['w']
        h = grammar['h']
        auto_scale = grammar.get('auto_scale', None)
        x_range = grammar.get('x_range', None)
        y_range = grammar.get('y_range', None)
        types = ChartGrammar.get_possible_chart_types()
        if chart_type not in types:
            raise UnknownChartType('%s is an unknown chart type. Possible '
                'chart types are %s' % (chart_type, ','.join(types)))
        return globals()[chart_type + 'Chart'](w, h, auto_scale=auto_scale,
            x_range=x_range, y_range=y_range)

    def download(self):
        pass

