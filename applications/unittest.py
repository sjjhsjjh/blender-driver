#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
# Module for mathematical operations.
# https://docs.python.org/3.5/library/math.html
from math import radians
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
import blender_driver.application.rest

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
    
    @property
    def restInterface(self):
        return self._application.restInterface
    
    @property
    def objectPath(self):
        return ('root','objects', self.id())
    
    def get_test_object(self):
        return self.application.get_test_object(self.id())
    
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, status):
        self._status = status
        self.application.set_test_text(self.id(), status)
    
    @property
    def store(self):
        return self.application.get_test_store(self.id()).store
    
    def setUp(self):
        super().setUp()
        try:
            skipReason = self.application.skipReasons[self.id()]
        except KeyError:
            skipReason = None
        if skipReason is not None:
            self.skipTest(skipReason)
    
    def skipTest(self, reason):
        self.application.skipReasons[self.id()] = reason
        super().skipTest(reason)

    def __init__(self, testCaseName, application):
        self._application = application
        self._skipReason = None
        super().__init__(testCaseName)

class Application(blender_driver.application.rest.Application):
    templates = {
        'cube': {
            'subtype':'Cube', 'physicsType':'RIGID_BODY',
            'location': (-4.0, -4.0, 4), 'scale':(0.25, 0.25, 0.25)},
        'floor': {
            'subtype':'Cube', 'physicsType':'STATIC',
            'location': (0, 0, 0), 'scale': (10, 10, 0.1)},
        'banner': {
            'text':"banner", 'location': (0, 0, 4)},
        'status': {
            'text':"status", 'location': (0, 0, 4),
            'scale':(0.5, 0.5, 0.5)}
    }
    
    banner = None
    terminatePerf = None

    @property
    def tickNumber(self):
        return self._tickNumber
    
    @property
    def restInterface(self):
        return self._restInterface
    
    # TestStore is used for persistent storage of data in between unit test
    # executions.
    class TestStore:
        def __init__(self):
            self.testObject = None
            self.skipReason = None
            self.testText = None
            self.store = {}

            self.offset = 0.0
    
    def get_test_store(self, testID):
        if testID not in self._testStore:
            testStore = self.TestStore()
            testStore.offset = self._testOffset
            self._testOffset -= 0.5
            self._testStore[testID] = testStore
        return self._testStore[testID]
    
    def get_test_object(self, testID):
        '''Only call after acquiring mainLock.'''
        testStore = self.get_test_store(testID)
        created = False
        if testStore.testObject is None:
            created = True
            testObject = self.game_add_object('cube')
            testObject.worldPosition.x = testStore.offset
            testObject.worldPosition.y = 4.0
            testStore.testObject = testObject

        return testStore.testObject, created
    
    def set_test_text(self, testID, text):
        statusText = testID if text is None else " ".join((testID, text))
        testStore = self.get_test_store(testID)
        if testStore.testText is None:
            testText = self.game_add_text('status')
            testText.rotation.x = 0.0
            testText.worldPosition = (testStore.offset, 0.0, 0.3)
            testStore.testText = testText

        textWidth = self.text_width(statusText) * self._textScale
        testStore.testText.text = statusText[:]
        testStore.testText.worldPosition.y = 3.5 - textWidth
    
    @property
    def skipReasons(self):
        return self._skipReasons

    # Override.
    def game_initialise(self):
        super().game_initialise()
        
        self.mainLock.acquire()
        try:
            self.banner = self.game_add_text('banner')
            self.banner.text = "Unit Tests"
            #
            # Add the floor object, which is handy to stop objects dropping out
            # of sight due to gravity. No need to access it later, so it doesn't
            # get put in the path store.
            self.game_add_object('floor')

            self._tickNumber = 0
            self._testStore = {}
            self._skipReasons = {}
            self._textScale = self.templates['status']['scale'][0]

            self._testOffset = 5.0
        finally:
            self.mainLock.release()

    # Override
    def game_tick_run(self):
        super().game_tick_run()
        self.mainLock.acquire()
        try:
            if self.terminatePerf is None:
                loader = TestLoaderWithApplication(self)
                suites = loader.discover(
                    os.path.join('applications', 'unittests'), "*.py")
                # for suite in suites:
                #     for test in suite:
                #         for case in test:
                #             print(case, type(case))
            else:
                if self.tickPerf < self.terminatePerf:
                    self.banner.text = (
                        "Unit Tests\nEnd:{:.2f} Now:{:.2f}".format(
                            self.terminatePerf, self.tickPerf))
                else:
                    self.game_terminate()
        finally:
            self.mainLock.release()

        if self.terminatePerf is None:
            results = unittest.TextTestRunner(
                verbosity=(2 if self.settings['arguments']['verbose'] else 1)
                # verbosity=2
            ).run(suites)
            self.mainLock.acquire()
            try:
                # Terminate if any test failed, or there were any errors, or if
                # all tests skipped, which is how they indicate completion.
                if (
                    len(results.errors) + len(results.failures) > 0
                    or len(results.skipped) >= results.testsRun
                ):
                    self.terminatePerf = self.tickPerf + 2.0

                self._tickNumber += 1
            finally:
                self.mainLock.release()
