#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Driver diagnostic.

This module contains analytical utilities that are used in some diagnostic and
demonstration Blender Driver applications."""

# Standard library imports, in alphabetic order.
#
# Module for column widths.
# https://docs.python.org/3/library/math.html
from math import log10

def timing_analysis_dump(times):
    return "\n".join(timing_analysis(times))

def timing_analysis(times, timePrecision=4):
    analyses = []
    indexWidth = index_width(times)
    timeWidth = field_width(times, precision=timePrecision)
    lastTime = None
    for index, time in enumerate(times):
        indexStr = '{:{indexWidth}d} '.format(index, indexWidth=indexWidth)
        timeStr = 'None'
        analysis = ""
        if time is not None:
            timeStr = '{:{timeWidth}.{timePrecision}f}'.format(
                time, timeWidth=timeWidth, timePrecision=timePrecision)
            if lastTime is not None:
                elapsed = time - lastTime
                analysis = ' {:.{timePrecision}f} 1/{:.0f}'.format(
                    elapsed, 0.0 if elapsed <= 0 else 1.0 / elapsed
                    , timePrecision=timePrecision)
            lastTime = time
        analyses.append(''.join((indexStr, timeStr, analysis)))
    return analyses

def index_width(lenable):
    return len("{:d}".format(len(lenable)- 1))

def field_width(values, precision=4, type="f"):
    width = None
    for value in values:
        if value is None:
            continue
        str = '{:.{precision}{type}}'.format(
            value, precision=precision, type=type)
        if width is None or len(str) > width:
            width = len(str)
    return width

def timing_summary(times, totalLabel="total", otherLabel="run"
                   , noneLabel="skipped"
                   ):
    nones = times.count(None)
    others = len(times) - nones
    return '{}:{:d} {}:{:d}({:.0%}) {}:{:d}({:.0%})'.format(
        totalLabel, len(times)
        , otherLabel, others, float(others) / float(len(times))
        , noneLabel, nones, float(nones) / float(len(times)))

def fall_analysis(positionsTimes):
    analyses = []
    lastPosition = None
    falls = 0
    indexWidth = index_width(positionsTimes)
    for index, positionTime in enumerate(positionsTimes):
        position, time = positionTime
        if lastPosition == position:
            fall = " ="
        else:
            fall = ""
            falls += 1
        lastPosition = position
            
        analyses.append('{:{indexWidth}d} {:.2f} {:.4f}{}'.format(
            index, position, time, fall, indexWidth=indexWidth))
    return len(analyses) - falls, "\n".join(analyses)

if __name__ == '__main__':
    print(__doc__)
    times = [0.0, 1.0, None, 2.5, 2.55, 10.0, 10.1, 10.3, 10.5, 10.7, 10.8]
    print("\nTest", times)
    print(timing_analysis_dump(times))
    print(timing_summary(times))
    print(timing_analysis_dump([]))

    raise SystemExit(1)
