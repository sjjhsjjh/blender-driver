#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver unit test that can be run from the unittest application.

This module is intended for use within Blender Driver and can only be used from
within Blender."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports would go here, in alphabetic order.
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication

class TestThread(TestCaseWithApplication):
    def test_thread(self):
        with self.application.mainLock:
            finish = self.application.tickPerf + 2.0
            self.show_status("{:.2f}".format(finish))
            counter = 0
        
        lastTick = None
        while self.application.tickPerf < finish:
            with self.tick:
                if lastTick is not None:
                    # Next line checks that the worker context can't be entered
                    # more than once in every game tick.
                    self.assertGreater(self.application.tickPerf, lastTick)
                lastTick = self.application.tickPerf
                with self.application.mainLock:
                    counter += 1
                    status = "{} {:.2f} {:.2f}".format(
                        counter, self.application.tickPerf, finish)
                    self.show_status(status)
                    if counter > 10 and self.application.tickPerf <= 0.0:
                        break
    
    def test_thread_second(self):
        self.test_thread()

    def test_error(self):
        with self.application.mainLock:
            pass
        with self.tick:
            empty = tuple()
            indexError = empty[1] # Intended error.
