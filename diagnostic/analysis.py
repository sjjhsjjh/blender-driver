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

def timing_analysis(times, timePrecision=4):
    analyses = []
    indexWidth = int(log10(len(times) - 1)) + 1
    timeWidth = None
    for time in times:
        if time is None:
            continue
        timeStr = '{:.{timePrecision}f}'.format(
            time, timePrecision=timePrecision)
        if timeWidth is None or len(timeStr) > timeWidth:
            timeWidth = len(timeStr)
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

def timing_analysis_dump(times):
    return "\n".join(timing_analysis(times))

def timing_summary(times, totalLabel="total", otherLabel="run"
                   , noneLabel="skipped"
                   ):
    nones = times.count(None)
    others = len(times) - nones
    return '{}:{:d} {}:{:d}({:.0%}) {}:{:d}({:.0%})'.format(
        totalLabel, len(times)
        , otherLabel, others, float(others) / float(len(times))
        , noneLabel, nones, float(nones) / float(len(times)))

if __name__ == '__main__':
    print(__doc__)
    times = [0.0, 1.0, None, 2.5, 2.55]
    print("\nTest", times)
    print(timing_analysis_dump(times))
    print(timing_summary(times))

    raise SystemExit(1)
