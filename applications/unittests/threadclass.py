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

# Standard library imports, in alphabetic order.
#
# Unit test module.
# https://docs.python.org/3/library/unittest.html
import unittest
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication

# Implicit test of two classes in different modules for thread tests.
class TestThreadClass(TestCaseWithApplication):
    def test_thread_fail(self):
        with self.application.mainLock:
            pass
        with self.tickLock:
            self.assertTrue(False) # Intended fail.
