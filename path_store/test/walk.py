#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestEdit
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
# Unit test module for mock subroutines.
# https://docs.python.org/3.5/library/unittest.mock.html
from unittest.mock import call, Mock
#
# Local imports.
#
# Modules under test.
import pathstore

def editor_void(point, path, results):
    return

def editor_append(point, path, results):
    results.append([point] + path)

class TestWalk(unittest.TestCase):
    def test_noop_editor(self):
        principal = 23.4

        walks = pathstore.walk(principal, editor_void, None)
        self.assertEqual(walks, 1)
        self.assertEqual(principal, 23.4)

        # Nothing but a pass.
        def editor_pass(point, path, results):
            pass
        walks = pathstore.walk(principal, editor_pass, None)
        self.assertEqual(walks, 1)
        self.assertEqual(principal, 23.4)

        def editor_none(point, path, results):
            return None
        walks = pathstore.walk(principal, editor_none, None)
        self.assertEqual(walks, 1)
        self.assertEqual(principal, 23.4)

        def editor_false(point, path, results):
            return False
        walks = pathstore.walk(principal, editor_false, None)
        self.assertEqual(walks, 1)
        self.assertEqual(principal, 23.4)

        unboundVariable = 20
        def editor_unbound(point, path, results):
            unboundVariable += 2
        with self.assertRaises(UnboundLocalError) as context:
            walks = pathstore.walk(principal, editor_unbound, None)
        self.assertEqual(
            str(context.exception)
            , "local variable 'unboundVariable' referenced before assignment")
        self.assertEqual(principal, 23.4)

    def test_scalar(self):
        principal = 4
        results = []
        walks = pathstore.walk(principal, editor_append, results)
        self.assertEqual(results, [[4]])
        self.assertEqual(principal, 4)
        
        del results[:]
        with self.assertRaises(TypeError) as context:
            walks = pathstore.walk(principal, editor_append, results, 0)
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in 4")

    def test_list(self):
        principal = [2, 3]
        walks = pathstore.walk(tuple(), editor_void)
        self.assertEqual(walks, 0)
    
        walks = pathstore.walk([], editor_void)
        self.assertEqual(walks, 0)
    
        principal0 = principal[:]
        results = []
        walks = pathstore.walk(principal0, editor_append, results)
        self.assertEqual(walks, 2)
        self.assertEqual(results, [[2,0], [3,1]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        
        principal0 = principal[:]
        del results[:]
        walks = pathstore.walk(principal0, editor_append, results, 1)
        self.assertEqual(walks, 1)
        self.assertEqual(results, [[3,1]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        
        with self.assertRaises(IndexError) as context:
            walks = pathstore.walk(principal, editor_void, None, 2)
        self.assertEqual(
            str(context.exception), "No point for 2 in {}".format(principal))
    
    def test_list_nested(self):
        principal = ['d', ['a', 'b'], 'c']
        # Deep copy by pasting.
        principal0 = ['d', ['a', 'b'], 'c']
        results = []
        
        walks = pathstore.walk(principal0, editor_append, results)
    
        self.assertEqual(walks, 4)
        self.assertEqual(results, [
            ['d', 0], ['a', 1, 0], ['b', 1, 1], ['c', 2]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
    
    def test_dict(self):
        principal = {'ef':'jape', 'gh': 'idol', 'kl': 'master'}
        principal0 = dict(principal)
        expected = [['idol', 'gh'], ['jape', 'ef'], ['master', 'kl']]
        expected.sort()
        
        results = []
        walks = pathstore.walk(principal0, editor_append, results)
        results.sort()
    
        self.assertEqual(walks, 3)
        self.assertEqual(results, expected)
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
    
        walks = pathstore.walk({}, editor_void)
        self.assertEqual(walks, 0)
    
    def test_list_dict(self):
        principal = [{'ef':'jape', 'gh': 'idol', 'kl': 'master'}, {'no':'yes'}]
        principal0 = [{'ef':'jape', 'gh': 'idol', 'kl': 'master'}, {'no':'yes'}]
        expected = [
            ['idol', 0, 'gh'], ['jape', 0, 'ef'], ['master', 0, 'kl'],
            ['yes', 1, 'no']]
        expected.sort()
        
        results = []
        walks = pathstore.walk(principal0, editor_append, results)
        results.sort()
    
        self.assertEqual(walks, 4)
        self.assertEqual(results, expected)
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
    
    def test_list_object(self):
        mock0 = Mock(spec_set=['attr'])
        mock0.attr = 11
        mock1 = Mock(mock0)
        mock1.attr = 13
        principal = [mock0, mock1]
    
        def editor_inc(point, path, results):
            point.attr += 1
            editor_append(point, path, results)
        testResults = []
        walks = pathstore.walk(principal, editor_inc, testResults)
        self.assertEqual(walks, 2)
        self.assertEqual(testResults, [[mock0,0], [mock1,1]])
        self.assertEqual(mock0.attr, 12)
        self.assertEqual(mock1.attr, 14)
    
        def editor_inc_if(point, path, results):
            if point.attr >= 14:
                point.attr += 1
                editor_append(point, path, results)
        testResults = []
        walks = pathstore.walk(principal, editor_inc_if, testResults)
        self.assertEqual(walks, 2)
        self.assertEqual(testResults, [[mock1,1]])
        self.assertEqual(mock0.attr, 12)
        self.assertEqual(mock1.attr, 15)

    def test_stop(self):
        principal = [2, 3, 4]

        def editor_stop(point, path, results):
            if point > 2:
                raise StopIteration
            editor_append(point, path, results)

        principal0 = principal[:]
        testResults = []
        walks = pathstore.walk(principal0, editor_stop, testResults)
        self.assertEqual(walks, 1)
        self.assertEqual(testResults, [[2,0]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)

        def editor_stop_after(point, path, results):
            editor_append(point, path, results)
            if point > 2:
                raise StopIteration

        principal0 = principal[:]
        del testResults[:]
        walks = pathstore.walk(principal0, editor_stop_after, testResults)
        self.assertEqual(walks, 1)
        self.assertEqual(testResults, [[2,0], [3,1]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
