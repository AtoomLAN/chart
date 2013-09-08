#!/usr/bin/env python

import codecs
import fcntl
import itertools
import math
import termios
import struct
import sys

class Chart(object):
    pass

class TerminalChart(Chart):
    def __init__(self, file=sys.stdout):
        self._file = codecs.getwriter('UTF-8')(file)

    @property
    def file(self):
        return self._file

    def draw(self, data, options=None):
        if not data:
            return

        if options is None:
            options = {}

        if "height" not in options:
            options["height"] = self._get_file_height()

        if "width" not in options:
            options["width"] = self._get_file_width()

        xs, ys = zip(*data)

        x_min, x_max = int(math.floor(min(xs))), int(math.ceil(max(xs)))
        x_str_len = self._str_len(x_min, x_max)

        y_min = int(math.floor(min(itertools.chain(*ys))))
        y_max = int(math.floor(max(itertools.chain(*ys))))
        y_str_len = self._str_len(y_min, y_max)

        if "title" in options:
            self.file.write(
                options["title"].center(x_max - x_min + y_str_len + 2) + "\n\n")
            options["height"] -= 2

        y_interval = max(int(math.ceil(
            (y_max - y_min) / (options["height"] - 2.0))), 1)
        
        self.file.write(str(y_max + y_interval).rjust(y_str_len) + u" \u2510")
        for y in ys:
            self._draw_bar(y, y_max + y_interval, y_interval)
        self.file.write("\n")

        for row in xrange(int(math.floor(y_max)), int(math.ceil(y_min - y_interval)), -y_interval):
            self.file.write(str(row).rjust(y_str_len) + u" \u2524")
            for y in ys:
                self._draw_bar(y, row, y_interval)
            self.file.write("\n")

        self.file.write(str(row - y_interval).rjust(y_str_len) + u" \u2534")

        for column in xrange(x_min, x_max + 1, x_str_len + 1):
            if column == x_max:
                self.file.write(u"\u2510")
            else:
                self.file.write(u"\u252c" +
                    min(x_str_len, x_max - column) * u"\u2500")

        self.file.write("\n")

        self.file.write(" " * (y_str_len + 2))
        for column in xrange(0, x_max - x_min + 1, x_str_len + 1):
            self.file.write(str(xs[column]).ljust(x_str_len + 1))

        self.file.write("\n")

        # if "comment" in options:
        #     self.file.write("\n")
        #     for line in options["comment"].splitlines():
        #         self.file.write(
        #             line.center(x_max - x_min + y_str_len + 2) + "\n")

    def _get_file_size(self):
        try:
            return struct.unpack('hh',
                fcntl.ioctl(file, termios.TIOCGWINSZ, '1234'))
        except:
            return 25, 80

    def _get_file_height(self):
        return self._get_file_size()[0]

    def _get_file_width(self):
        return self._get_file_size()[1]

    def _draw_bar(self, y, row, interval):
        y_min, y_max = min(y), max(y)
        
        if y_min >= row + 0.5 * interval:
            self.file.write(u"\u2503")
        elif y_max >= row + 0.5 * interval:
            if y_min >= row:
                self.file.write(u"\u257d")
            else:
                self.file.write(u"\u2502")
        elif y_min >= row:
            self.file.write(u"\u257b")
        elif y_max >= row:
            self.file.write(u"\u2577")
        else:
            self.file.write(u" ") 

    def _str_len(self, min_value, max_value):
        return int(math.ceil(
            max(
                math.log(abs(min_value) + sys.float_info.min, 10)
              , math.log(abs(max_value) + sys.float_info.min, 10)
            )
        )) + int(min_value < 0)

if __name__ == "__main__":
    data = (
        (1, (59, 66)),
        (2, (53, 63)),
        (3, (59, 67)),
        (4, (58, 58)),
        (5, (61, 70)),
        (6, (68, 71)),
        (7, (57, 66)),
        (8, (75, 81)),
        (9, (64, 69)),
        (10, (57, 58)),
        (11, (69, 79)),
        (12, (59, 59)),
        (13, (53, 63)),
        (14, (65, 65)),
        (15, (71, 71)),
        (16, (60, 63)),
        (17, (57, 67)),
        (18, (68, 70)),
        (19, (62, 69)),
        (20, (60, 67)),
        (21, (58, 67)),
        (22, (57, 61)),
        (23, (64, 69)),
        (24, (62, 69)),
        (25, (68, 71)),
        (26, (61, 64)),
        (27, (57, 64)),
        (28, (72, 73)),
        (29, (61, 67)),
        (30, (68, 73)),
        (31, (70, 72)),
        (32, (55, 63)),
        (33, (71, 75)),
        (34, (62, 68)),
        (35, (74, 76)),
        (36, (58, 68)),
        (37, (62, 69)),
        (38, (59, 69)),
        (39, (59, 63)),
        (40, (62, 62)),
        (41, (73, 77)),
        (42, (55, 64)),
        (43, (50, 60)),
        (44, (73, 78)),
        (45, (63, 65)),
        (46, (74, 78)),
        (47, (70, 72)),
        (48, (63, 66)),
        (49, (69, 79)),
        (50, (64, 66)),
        (51, (61, 64)),
        (52, (57, 63)),
        (53, (50, 59)),
        (54, (60, 62)),
        (55, (53, 62)),
        (56, (57, 66)),
        (57, (60, 61)),
        (58, (64, 73))
    )
    options = {
        "height": 24,
        "title": "CPU% per minute (last 60 minutes)",
        "width": 80,
    }

    terminal_chart = TerminalChart()
    # terminal_chart.draw(data, options)

    import rrdtool

    data = rrdtool.fetch("chart.rrd", "LAST", "-r 60", "-s -1h")
    data = filter(lambda x: not None in x[1], zip(xrange((data[0][1] - data[0][0]) / data[0][2]), reversed(data[2])))

    terminal_chart.draw(data, options)

