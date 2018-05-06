#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Driver diagnostic.

This module contains analytical utilities that are used in some diagnostic and
demonstration Blender Driver applications."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for column widths.
# https://docs.python.org/3/library/math.html
from math import log10

def timing_analysis(times):
    analyses = []
    indexWidth = int(log10(len(times) - 1)) + 1
    timePrecision = 4
    timeWidth = int(log10(times[-1])) + 2 + timePrecision
    for index, tickTime in enumerate(times):
        base = '{:{indexWidth}d} {:{timeWidth}.{timePrecision}f}'.format(
            index, tickTime, indexWidth=indexWidth, timeWidth=timeWidth
            , timePrecision=timePrecision)
        analysis = ""
        if index > 0:
            elapsed = tickTime - times[index - 1]
            analysis = ' {:.{timePrecision}f} 1/{:.0f}'.format(
                elapsed, 0.0 if elapsed <= 0 else 1.0 / elapsed
                , timePrecision=timePrecision)
        analyses.append(''.join((base, analysis)))
    return analyses

def timing_analysis_dump(times):
    return "\n".join(timing_analysis(times))
