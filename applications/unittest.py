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
# https://docs.python.org/3/library/argparse.html
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
# https://docs.python.org/3/library/threading.html
import threading
#
# Module for pretty printing exceptions.
# https://docs.python.org/3/library/traceback.html
import traceback
#
# Unit test module.
# https://docs.python.org/3/library/unittest.html
import unittest
#
# Local imports.
#
# Application base class module.
import blender_driver.application.rest
#
# Tick time dumper.
from diagnostic.analysis import timing_summary

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
    def tick(self):
        '''Context manager for each game tick.'''
        return self.application.worker(self.id())
    
    @property
    def phases(self):
        return self._phases
    
    def add_phase_starts(self, *args):
        for start in args:
            self._phases.append(self.application.tickPerf + float(start))
            
    def add_phase_offsets(self, *args):
        start = self._phases[-1]
        for offset in args:
            start += float(offset)
            self._phases.append(start)
            
    def up_to_phase(self, phase):
        return self.application.tickPerf < self._phases[phase]
    
    def run(self, result=None):
        # mainLock cannot be acquired here.
        self.show_status(None)
        return super().run(result)
    
    def __init__(self, testCaseName, application):
        self._application = application
        self._phases = []
        super().__init__(testCaseName)

class ThreadTestResult(unittest.TestResult):
    
    class Worker:
        def __init__(self, scheduler):
            self._scheduler = scheduler
            self._state = True
            self._lock = threading.Lock()
            self._thread = threading.current_thread()
        
        @property
        def state(self):
            return self._state
        @state.setter
        def state(self, state):
            self._state = state
            
        @property
        def thread(self):
            return self._thread
        @thread.setter
        def thread(self, thread):
            self._thread = thread
        
        @property
        def lock(self):
            return self._lock
        
        def __repr__(self):
            locked = None
            if self._lock is not None:
                if self._lock.acquire(False):
                    locked = False
                    self._lock.release()
                else:
                    locked = True
            repr = {'locked':locked,
                    'state':self._state,
                    'threadName':self.threadName}
            return repr.__repr__()
        
        # Context Manager implementation
        # https://docs.python.org/3/reference/datamodel.html#object.__enter__
        def __enter__(self):
            # print("Worker", self.thread, "Enter", 0)
            self._lock.release()
            # print("Worker", self.thread, "Enter", 1)
            self._scheduler.event.wait()
            # print("Worker", self.thread, "Enter", 2)
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            # print("Worker", self.thread, "Exit", 0)
            self._lock.acquire()
            # print("Worker", self.thread, "Exit", 1)
            self._scheduler.barrier.wait()
            # print("Worker", self.thread, "Exit", 2)
            return False
    
        @property
        def threadName(self):
            if self._thread is None:
                return None
            return self._thread.name
    
    class Scheduler:
        def __init__(self, lock, workers):
            self._workers = workers
            self._lock = lock
            
            self._barrier = threading.Barrier(1)
            # Next line should prevent any worker from waiting before the
            # barrier has been set up with the correct number of parties.
            self._barrier.abort()
            
            self._event = threading.Event()
            self._event.clear()

        @property
        def event(self):
            return self._event
        
        @property
        def barrier(self):
            return self._barrier
        
        def start_barrier(self, tests):
            if self._barrier.parties == tests + 1:
                self._barrier.reset()
            else:
                self._barrier = threading.Barrier(tests + 1)
            return self._barrier
        
        def abort(self):
            self._barrier.abort()
            self._event.set()
        
        # Context Manager implementation
        # https://docs.python.org/3/reference/datamodel.html#object.__enter__
        def __enter__(self):
            # print("Scheduler", "Enter", 0)
            running = 0
            # print("Scheduler", "Enter", 1)
            for worker in self._workers.values():
                worker.lock.acquire()
                if worker.state:
                    running += 1
                else:
                    if worker.thread is not None:
                        worker.thread.join()
                        worker.thread = None
            # print("Scheduler", "Enter", 2, running)
            self.start_barrier(running)
            self._event.set()
            for worker in self._workers.values():
                worker.lock.release()
            self._event.clear()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            # print("Scheduler", "Exit", 0)
            self._barrier.wait()
            # print("Scheduler", "Exit", 1)
            return False

    # Next couple of method overrides do something.
    def startTest(self, test):
        with self._lock:
            self._anyStarted = True
            worker = self.Worker(self._scheduler)
            worker.lock.acquire()
            self._workers[test.id()] = worker
        self._scheduler.barrier.wait()
        with self._lock:
            return super().startTest(test)

    def stopTest(self, test):
        # print(test.id(), "stopTest")
        with self._lock:
            worker = self._workers[test.id()]
            worker.state = False
            worker.lock.release()
            return super().stopTest(test)

    # Remaining method overrides only add a status display and synchronisation.
    def addError(self, test, err):
        test.show_status("error")
        with self._lock:
            # traceback.print_exception(*err)
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
            return self._workers
    
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
    def scheduler(self):
        return self._scheduler
    
    @property
    def allStopped(self):
        with self._lock:
            if not self._anyStarted:
                return False
            for worker in self._workers.values():
                if worker.state:
                    return False
            return True
    
    def worker(self, testIdentifier):
        return self._workers[testIdentifier]
    
    def __init__(self):
        super().__init__()
        self._anyStarted = False
        self._lock = threading.Lock()
        self._workers = {}
        self._scheduler = self.Scheduler(self._lock, self._workers)

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
        threads = []
        for suite in suites:
            for test in suite:
                for case in test:
                    threads.append(threading.Thread(
                        target=case.run, args=(result,), name=case.id()))
        
        # It might be better to initialise the barrier based on:
        # suites.countTestCases()
        # However, at the point that I realised that, it was working as it is
        # now and I didn't want to touch it. If the barrier was initialised
        # before the loop, the start() calls could be in the loop instead of
        # below.
        barrier = result.scheduler.start_barrier(len(threads))

        for index, thread in enumerate(threads):
            # print("ThreadTestRunner", index)
            thread.start()
        # print("ThreadTestRunner", "Waiting...")
        barrier.wait()
        # print("ThreadTestRunner", "Waited")

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
        'banner': {
            'text':"banner", 'location': (0, 0, 4)},
        'status': {
            'text':"status", 'location': (0, 0, 0.3),
            'scale':(0.5, 0.5, 0.5)}
    }
    
    banner = None
    
    # Proxy for getting the test lock from the TestCase method, which can't
    # access the results object directly.
    def worker(self, testIdentifier):
        return self._results.worker(testIdentifier)

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
        '''Only call if mainLock has been acquired.'''
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
    
    def _discover_test_suites(self):
        loader = TestLoaderWithApplication(self)
        discoveredSuites = loader.discover(
            os.path.join('applications', 'unittests'), "*.py")

        if len(self.arguments.tests) <= 0:
            return discoveredSuites

        # Couldn't see any way to remove tests from a TestSuite. The following
        # code creates a new empty suite and then adds only the tests that match
        # the specification.
        suites = unittest.TestSuite()
        knownTests = []
        for suite in discoveredSuites:
            add = False
            for test in suite:
                for case in test:
                    className = case.__class__.__name__
                    if className not in knownTests:
                        knownTests.append(className)
                    if className in self.arguments.tests:
                        add = True
            if add:
                suites.addTest(suite)

        if suites.countTestCases() <= 0:
            raise ValueError(
                'No tests match specification:{}. Known tests:{}.'.format(
                self.arguments.tests, knownTests))
        return suites
    
    # Override.
    def game_initialise(self):
        super().game_initialise()
        self._results = None
        self._terminatePerf = None
        self._tickTimes = []
        self._lastCompletion = None
        self._lastCompletionTick = None
        
        with self.mainLock:
            self.banner = self.game_add_text('banner')
            self.banner.text = "Unit Tests"

            self._textScale = self.templates['status']['scale'][0]

            self._testRootPath = ('root','test')

            self._testObjectOffset = 5.0
            self._testObjectIncrement = -0.5
            self._results = ThreadTestRunner(
                verbosity=2 if self.settings['arguments']['verbose'] else 1
            ).run(self._discover_test_suites())
            print("Number of threads:{}.".format(threading.active_count()))

    # Override
    def game_terminate(self):
        if self._terminatePerf is None and self._results is not None:
            # An error must have occurred.
            self._results.scheduler.abort()
        super().game_terminate()
        if self._results is not None:
            print(self._results.formatted)
            print('Tick time analysis: interval:{:d} {}.'.format(
                self.tickInterval, timing_summary(self._tickTimes)))

    # Override
    def game_tick_run(self):
        super().game_tick_run()
        self._tickTimes.append(self.tickPerf)
        if self._terminatePerf is None:
            with self._results.scheduler:
                with self.mainLock:
                    self.banner.text = (
                        "Unit Tests tickInterval:{:d}\nNow:{:.2f}".format(
                            self.tickInterval, self.tickPerf))
                if self._results.allStopped:
                    print('Tests stopped at:{:.2f}'.format(self.tickPerf))
                    self._terminatePerf = self.tickPerf + 2.0
        else:
            with self.mainLock:
                if self.tickPerf < self._terminatePerf:
                    self.banner.text = (
                        "Unit Tests End:{:.2f}\nNow:{:.2f}".format(
                            self._terminatePerf, self.tickPerf))
                else:
                    self.game_terminate()

    def tick_skipped(self):
        self._tickTimes.append(None)

    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.add_argument(
            'tests', nargs='*', type=str, help=
            "Tests to run. Default is to run all.")
        return parser

    @property
    def lastCompletion(self):
        return self._lastCompletion
    @property
    def lastCompletionTick(self):
        return self._lastCompletionTick

    # Override.
    def print_completions_log(self, anyCompletions, logStore):
        if anyCompletions:
            self._lastCompletionTick = self.tickPerf
            self._lastCompletion = "{:.4f} completions:{}".format(
                self.tickPerf, logStore)
