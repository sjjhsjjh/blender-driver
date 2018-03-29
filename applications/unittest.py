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
# https://docs.python.org/3/library/math.html
from math import radians
#
# Module for building paths, which is only used to build a unittest discover
# path.
# https://docs.python.org/3/library/os.path.html
import os.path
#
# Module for threads and locks.
# https://docs.python.org/3/library/threading.html#thread-objects
import threading
#
# Unit test module.
# https://docs.python.org/3/library/unittest.html
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
    
    def add_test_object(self):
        return self.application.add_test_object(self.id())
    
    def show_status(self, message):
        self.application.show_test_status(self.id(), message)

    @property
    def tickLock(self):
        '''Lock that is released every tick.'''
        return self.application.tick_test_lock(self.id())
    
    def run(self, result=None):
        self.show_status(None)
        return super().run(result)
    
    def __init__(self, testCaseName, application):
        self._application = application
        super().__init__(testCaseName)

class ThreadTestResult(unittest.TestResult):
    
    class TestState(object):
        def __init__(self):
            self.lock = threading.Lock()
            self.stopped = False
            self.thread = threading.current_thread()
        
        @property
        def threadName(self):
            if self.thread is None:
                return None
            return self.thread.name
        
        def __repr__(self):
            locked = None
            if self.lock is not None:
                if self.lock.acquire(False):
                    locked = False
                    self.lock.release()
                else:
                    locked = True
            repr = {'locked':locked,
                    'stopped':self.stopped,
                    'threadName':self.threadName}
            return repr.__repr__()

    # Next couple of method overrides do something.
    def startTest(self, test):
        with self._lock:
            self._anyStarted = True
            identifier = test.id()
            self._testStates[identifier] = self.TestState()
            #
            # Acquire every tick lock before the test can run.
            self.tick_test_lock(identifier).acquire()
        return super().startTest(test)

    def stopTest(self, test):
        with self._lock:
            self._testStates[test.id()].stopped = True
        return super().stopTest(test)

    # Remaining method overrides only add a status display and synchronisation.
    def addError(self, test, err):
        test.show_status("error")
        with self._lock:
            return super().addError(test, err)

    def addFailure(self, test, err):
        test.show_status("fail")
        with self._lock:
            return super().addFailure(test, err)

    def addSuccess(self, test):
        test.show_status("OK")
        with self._lock:
            return super().addSuccess(test)

    def addSkip(self, test, reason):
        test.show_status("skip")
        with self._lock:
            return super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        test.show_status("expected fail")
        with self._lock:
            return super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        test.show_status("unexpected success")
        with self._lock:
            return super().addUnexpectedSuccess(test)

    def addSubTest(self, test, subtest, outcome):
        with self._lock:
            return addSubTest(test, subtest, outcome)

    def state(self):
        with self._lock:
            return self._testStates
    
    def __repr__(self):
        with self._lock:
            return super().__repr__()
    
    @property
    def formatted(self):
        with self._lock:
            return '\n'.join(
                ('Passed:{}'.format(
                        self.testsRun - (len(self.errors)
                                         + len(self.failures))),) +
                tuple(
                    'error[{}] {}\n{}'.format(
                        index+1, error[0], error[1]
                    ) for index, error in enumerate(self.errors)) +
                tuple(
                    'failure[{}] {}\n{}'.format(
                        index+1, failure[0], failure[1]
                    ) for index, failure in enumerate(self.failures)))
    
    @property
    def allStopped(self):
        with self._lock:
            if not self._anyStarted:
                return False
            for testState in self._testStates.values():
                if not testState.stopped:
                    return False
            return True
    
    def tick_test_lock(self, testIdentifier):
        return self._testStates[testIdentifier].lock
    
    def tick_release(self):
        for testState in self._testStates.values():
            testState.lock.release()
    
    def tick_acquire(self):
        for testState in self._testStates.values():
            testState.lock.acquire()

    def finish(self):
        if not self.allStopped:
            return False
        with self._lock:
            for testState in self._testStates.values():
                if testState.thread is not None:
                    testState.thread.join()
                    testState.thread = None
            return True

    def __init__(self):
        super().__init__()
        self._anyStarted = False
        self._lock = threading.Lock()
        self._testStates = {}

# Seems like a good idea to make this a subclass of TextTestRunner, although it
# doesn't ever call super().
class ThreadTestRunner(unittest.TextTestRunner):
    def run(self, suites):
        #
        # The result object will manage the test case threads.
        result = ThreadTestResult()
        #
        # Each test will register itself in the result object, in its startTest
        # call. All this code needs to do is spawn a thread.
        for suite in suites:
            for test in suite:
                for case in test:
                    threading.Thread(
                        target=case.run, args=(result,), name=case.id()
                    ).start()

        # Following code would merge a bunch of TestResult objects together. It
        # seemed better to implement a TestResult subclass with a lock, i.e. a
        # thread safe one, which is what's in ThreadTestResult, above.
        #
        # result = unittest.TestResult()
        # for runningTest in runningTests:
        #     for property_ in (
        #         'errors', 'failures', 'skipped', 'expectedFailures',
        #         'unexpectedSuccesses'
        #     ):
        #         getattr(result, property_).extend(
        #             getattr(runningTest.result, property_))
        #     result.testsRun += runningTest.result.testsRun

        return result

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
            'text':"status", 'location': (0, 0, 0.3),
            'scale':(0.5, 0.5, 0.5)}
    }
    
    banner = None
    terminatePerf = None
    
    # Proxy for getting the test lock from the TestCase method, which can't
    # access the results object directly.
    def tick_test_lock(self, testIdentifier):
        return self._results.tick_test_lock(testIdentifier)

    @property
    def restInterface(self):
        return self._restInterface
    
    def get_test_offset(self, testIdentifier):
        path = self._testRootPath + (testIdentifier, 'offset')
        try:
            offset = self._restInterface.rest_get(path)
        except KeyError:
            offset = self._testObjectOffset
            self._testObjectOffset += self._testObjectIncrement
            self._restInterface.rest_put(offset, path)
        return offset
    
    def add_test_object(self, testIdentifier):
        '''Only call after acquiring mainLock.'''
        testObject = self.game_add_object('cube')
        testObject.worldPosition.x = self.get_test_offset(testIdentifier)
        testObject.worldPosition.y = 4.0
        return testObject
    
    def show_test_status(self, testIdentifier, message):
        path = self._testRootPath + (testIdentifier, 'status')
        try:
            status = self._restInterface.rest_get(path)
        except KeyError:
            status = self.game_add_text('status')
            status.rotation.x = 0.0
            status.worldPosition.x = self.get_test_offset(testIdentifier)
            self._restInterface.rest_put(status, path)
        
        statusText = (testIdentifier if message is None else (
            " ".join((testIdentifier, message))))

        textWidth = self.text_width(statusText) * self._textScale
        status.text = statusText[:]
        status.worldPosition.y = 3.5 - textWidth
    
    # Override.
    def game_initialise(self):
        super().game_initialise()
        
        with self.mainLock:
            self.banner = self.game_add_text('banner')
            self.banner.text = "Unit Tests"
            #
            # Add the floor object, which is handy to stop objects dropping out
            # of sight due to gravity. No need to access it later, so it doesn't
            # get put in the path store.
            self.game_add_object('floor')

            self._textScale = self.templates['status']['scale'][0]

            self._testRootPath = ('root','test')

            self._testObjectOffset = 5.0
            self._testObjectIncrement = -0.5

            loader = TestLoaderWithApplication(self)
            suites = loader.discover(
                os.path.join('applications', 'unittests'), "*.py")
            self._results = ThreadTestRunner(
                verbosity=(2 if self.settings['arguments']['verbose'] else 1)
            ).run(suites)

    # Override
    def game_tick_run(self):
        super().game_tick_run()
        if self.terminatePerf is None:
            self._results.tick_release()

            with self.mainLock:
                self.banner.text = (
                    "Unit Tests\nNow:{:.2f}".format(self.tickPerf))

            if self._results.allStopped:
                print('Tests stopped at:{:.2f}'.format(self.tickPerf))
                if self._results.finish():
                    self.terminatePerf = self.tickPerf + 2.0
                    print(self._results.formatted)
                else:
                    print("Tests couldn't finish"
                          , self._results, self._results.state)

            self._results.tick_acquire()
        else:
            with self.mainLock:
                if self.tickPerf < self.terminatePerf:
                    self.banner.text = (
                        "Unit Tests End:{:.2f}\nNow:{:.2f}".format(
                            self.terminatePerf, self.tickPerf))
                else:
                    self.game_terminate()
