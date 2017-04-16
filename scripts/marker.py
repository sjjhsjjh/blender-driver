#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Script to start Blender and Blender Driver, and a specific Blender Driver
application.

This script is built on the main Blender Driver start script.
"""
# Standard library imports, in alphabetic order.
#
# Module for file and directory paths.
# https://docs.python.org/3.5/library/os.path.html
from os.path import basename, splitext
#
# Module for access to the command line.
# https://docs.python.org/3.5/library/sys.html
import sys
#
# Local imports.
#
# Script to create Blender Driver command line.
from blenderdriver import main

# Set the application module name from the name of this script, without the
# extension.
application = splitext(basename(__file__))[0]

main(sys.argv + [
    '--start'
    , '--applicationModule', ".".join(('applications', application))
    , '--'
    , '--minScale', "1.0"
    , '--changeScale', "0.75"
    , '--circuit'
    , '--sleep', "0.01"])
