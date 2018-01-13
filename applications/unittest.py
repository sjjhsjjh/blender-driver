#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver Application with Python unit test integration.

This module is intended for use within Blender Driver and can only be used from
within Blender."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for command line switches.
# https://docs.python.org/3.5/library/argparse.html
# The import isn't needed because this class uses the base class to get an
# object.
# import argparse
#
# Unit test module.
# https://docs.python.org/3.5/library/unittest.html
import unittest
#
# Local imports.
#
# Application base class module.
import blender_driver.application.base
#
# Unit test modules.
from applications.unittests.gameobject import TestGameObject

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))

class Application(blender_driver.application.base.Application):
    templates = {
        'cube': {
            'subtype':'Cube', 'physicsType':'RIGID_BODY',
            'location': (0, 0, 4), 'scale': (0.2, 0.2, 0.2)}
    }

    # Override
    def game_tick(self):
        TestGameObject.set_application(self)
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestGameObject)
        unittest.TextTestRunner().run(suite)
        self.game_terminate()
