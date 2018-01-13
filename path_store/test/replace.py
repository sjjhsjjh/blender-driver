#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""\
Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestReplace
"""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Unit test module.
# https://docs.python.org/3.5/library/unittest.html
import unittest
#
# Local imports.
#
# Modules under test.
import pathstore

class TestReplace(unittest.TestCase):
    def test_into_none(self):
        value = {'kiki':"valoo", 'ikik':"valet"}
        parent = pathstore.replace(None, value)
        self.assertIs(parent, value)
    
    def test_at_path(self):
        parent0 = {'kiki':"valoo", 'ikik':"valet"}
        #
        # Put an object into the dictionary.
        class Principal:
            pass
        value = Principal()
        value.beeb = "quib"
        parent1 = pathstore.replace(parent0, value, 'ikik')
        self.assertIs(parent1, parent0)
        self.assertIs(pathstore.get(parent1, 'ikik'), value)
        self.assertIs(parent1['ikik'], value)
        #
        # Put a dictionary into the dictionary instead.
        value = {'leel':"wab", 'lahal': "amb"}
        parent1 = pathstore.replace(parent0, value, 'ikik')
        self.assertIs(parent1, parent0)
        self.assertIs(pathstore.get(parent1, 'ikik'), value)
        self.assertIs(parent1['ikik'], value)

# Put in an object where the (default) point maker would have put a dictionary.