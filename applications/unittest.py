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
# Module for building paths, which is only used to build a unittest discover
# path.
# https://docs.python.org/3.5/library/os.path.html
import os.path
#
# Unit test module.
# https://docs.python.org/3.5/library/unittest.html
import unittest
#
# Local imports.
#
# Application base class module.
import blender_driver.application.base

# Diagnostic print to show when it's imported, if all its own imports run OK.
print("".join(('Application module "', __name__, '" ')))


# TOTH: https://stackoverflow.com/a/37916673/7657675
class TestLoaderWithApplication(unittest.TestLoader):
    '''\
    Custom test loader that gets a Blender Driver application instance and
    passes it to all test case classes.
    '''

    # Override.
    def loadTestsFromTestCase(self, testCaseClass):
        '''Return a suite of all tests cases contained in testCaseClass.'''
        # print('"'.join(('Loading ', testCaseClass.__name__, '.')))

        testCaseNames = self.getTestCaseNames(testCaseClass)
        if (not testCaseNames) and hasattr(testCaseClass, 'runTest'):
            testCaseNames = ['runTest']
    
        return self.suiteClass([
            testCaseClass(testCaseName, self._application
                          ) for testCaseName in testCaseNames])
    
    def __init__(self, application):
        self._application = application
        # ToDo: Handle other constructor options for TestLoader.

class TestCaseWithApplication(unittest.TestCase):
    @property
    def application(self):
        return self._application

    def __init__(self, testCaseName, application):
        self._application = application
        super().__init__(testCaseName)

class Application(blender_driver.application.base.Application):
    templates = {
        'cube': {
            'subtype':'Cube', 'physicsType':'RIGID_BODY',
            'location': (0, 0, 4), 'scale': (0.2, 0.2, 0.2)}
    }

    # Override
    def game_tick(self):
        loader = TestLoaderWithApplication(self)
        suites = loader.discover(os.path.join('applications', 'unittests')
                                 , "*.py")
        unittest.TextTestRunner(
            verbosity=(2 if self.settings['arguments']['verbose'] else 1)
            ).run(suites)
        self.game_terminate()
