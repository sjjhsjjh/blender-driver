#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestWalk
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
from unittest.mock import Mock
#
# Local imports.
#
# Modules under test.
import pathstore

def editor_void(point, path, results):
    '''Implicit return of None.'''
    return

def editor_append(point, path, results):
    '''Implicit return of None.'''
    results.append([point] + path)

class TestWalk(unittest.TestCase):
    def test_noop_editor(self):
        principal0 = 23.4

        mock = Mock(side_effect=editor_void)
        principal = pathstore.walk(principal0, mock)
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(principal, 23.4)
        self.assertIs(principal, principal0)

        def editor_none(point, path, results):
            return None
        mock = Mock(side_effect=editor_none)
        principal = pathstore.walk(principal0, mock)
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(principal, 23.4)
        self.assertIs(principal, principal0)

        def editor_false(point, path, results):
            return False
        mock = Mock(side_effect=editor_false)
        principal = pathstore.walk(principal0, mock)
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(principal, 23.4)
        self.assertIs(principal, principal0)

        unboundVariable = 20
        def editor_unbound(point, path, results):
            unboundVariable += 2
        with self.assertRaises(UnboundLocalError) as context:
            principal = pathstore.walk(principal0, editor_unbound)
        self.assertEqual(
            str(context.exception)
            , "local variable 'unboundVariable' referenced before assignment")
        self.assertIs(principal, principal0)

    def test_scalar(self):
        principal0 = 4
        results = []
        principal = pathstore.walk(principal0, editor_append, results=results)
        self.assertEqual(results, [[4]])
        self.assertEqual(principal, 4)
        self.assertIs(principal, principal0)
        
        del results[:]
        with self.assertRaises(TypeError) as context:
            principal = pathstore.walk(principal0, editor_append, 0, results)
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in 4")

    def test_list(self):
        principal0 = tuple()
        mock = Mock(side_effect=editor_void)
        principal = pathstore.walk(principal0, mock)
        self.assertIs(principal, principal0)
        self.assertEqual(len(principal), 0)
        self.assertEqual(mock.call_count, 0)
    
        principal0 = []
        mock = Mock(side_effect=editor_void)
        principal = pathstore.walk(principal0, mock)
        self.assertIs(principal, principal0)
        self.assertEqual(len(principal), 0)
        self.assertEqual(mock.call_count, 0)
    
        principal = [2, 3]

        principal0 = principal[:]
        results = []
        mock = Mock(side_effect=editor_append)
        principal1 = pathstore.walk(principal0, mock, results=results)
        self.assertEqual(mock.call_count, 2)
        self.assertEqual(results, [[2,0], [3,1]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        self.assertIs(principal0, principal1)
        
        principal0 = principal[:]
        del results[:]
        mock = Mock(side_effect=editor_append)
        principal1 = pathstore.walk(principal0, mock, 1, results)
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(results, [[3,1]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        self.assertIs(principal0, principal1)

        expected = IndexError(
            "Couldn't get point for 2 in {}".format(principal))
        with self.assertRaises(type(expected)) as context:
            principal1 = pathstore.walk(principal0, editor_void, 2)
        self.assertEqual(str(context.exception), str(expected))
    
    def test_list_nested(self):
        principal = ['d', ['a', 'b'], 'c']
        # Deep copy by pasting.
        principal0 = ['d', ['a', 'b'], 'c']
        results = []
        
        mock = Mock(side_effect=editor_append)
        # Next line has positional path=None.
        principal1 = pathstore.walk(principal0, mock, None, results)
    
        self.assertEqual(mock.call_count, 4)
        self.assertEqual(results, [
            ['d', 0], ['a', 1, 0], ['b', 1, 1], ['c', 2]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        self.assertIs(principal0, principal1)
    
    def test_dict(self):
        principal0 = {}
        mock = Mock(side_effect=editor_void)
        principal1 = pathstore.walk(principal0, mock)
        self.assertIs(principal1, principal0)
        self.assertEqual(len(principal0.keys()), 0)
        self.assertEqual(mock.call_count, 0)

        principal = {'ef':'jape', 'gh': 'idol', 'kl': 'master'}
        principal0 = dict(principal)
        expected = [['idol', 'gh'], ['jape', 'ef'], ['master', 'kl']]
        expected.sort()
        
        results = []
        mock = Mock(side_effect=editor_append)
        principal1 = pathstore.walk(principal0, mock, results=results)
        results.sort()
    
        self.assertEqual(mock.call_count, 3)
        self.assertEqual(results, expected)
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        self.assertIs(principal0, principal1)

        mock = Mock(side_effect=editor_append)
        principal1 = pathstore.walk(principal0, mock, 'gh', results)
        self.assertEqual(mock.call_count, 1)
        self.assertIs(principal0, principal1)
    
    def test_list_dict(self):
        principal = [{'ef':'jape', 'gh': 'idol', 'kl': 'master'}, {'no':'yes'}]
        principal0 = [{'ef':'jape', 'gh': 'idol', 'kl': 'master'}, {'no':'yes'}]
        expected = [
            ['idol', 0, 'gh'], ['jape', 0, 'ef'], ['master', 0, 'kl'],
            ['yes', 1, 'no']]
        expected.sort()
        
        results = []
        mock = Mock(side_effect=editor_append)
        principal1 = pathstore.walk(principal0, mock, results=results)
        results.sort()
    
        self.assertEqual(mock.call_count, 4)
        self.assertEqual(results, expected)
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        self.assertIs(principal0, principal1)
    
    def test_list_object(self):
        mock0 = Mock(spec_set=['attr'])
        mock0.attr = 11
        mock1 = Mock(mock0)
        mock1.attr = 13
        principal0 = [mock0, mock1]
    
        def editor_inc(point, path, results):
            point.attr += 1
            editor_append(point, path, results)
        testResults = []
        mock = Mock(side_effect=editor_inc)
        principal1 = pathstore.walk(principal0, mock, results=testResults)
        self.assertEqual(mock.call_count, 2)
        self.assertEqual(testResults, [[mock0,0], [mock1,1]])
        self.assertEqual(mock0.attr, 12)
        self.assertEqual(mock1.attr, 14)
        self.assertIs(principal0, principal1)
    
        def editor_inc_if(point, path, results):
            if point.attr >= 14:
                point.attr += 1
                editor_append(point, path, results)
        testResults = []
        mock = Mock(side_effect=editor_inc_if)
        principal1 = pathstore.walk(principal0, mock, results=testResults)
        self.assertEqual(mock.call_count, 2)
        self.assertEqual(testResults, [[mock1,1]])
        self.assertEqual(mock0.attr, 12)
        self.assertEqual(mock1.attr, 15)
        self.assertIs(principal0, principal1)

    def test_stop(self):
        principal = [2, 3, 4]

        def editor_stop(point, path, results):
            if point > 2:
                raise StopIteration
            editor_append(point, path, results)

        principal0 = principal[:]
        testResults = []
        mock = Mock(side_effect=editor_stop)
        principal1 = pathstore.walk(principal0, mock, results=testResults)
        self.assertEqual(mock.call_count, 2)
        self.assertEqual(testResults, [[2,0]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        self.assertIs(principal0, principal1)

        def editor_stop_after(point, path, results):
            editor_append(point, path, results)
            if point > 2:
                raise StopIteration

        principal0 = principal[:]
        del testResults[:]
        mock = Mock(side_effect=editor_stop_after)
        principal1 = pathstore.walk(principal0, mock, results=testResults)
        self.assertEqual(mock.call_count, 2)
        self.assertEqual(testResults, [[2,0], [3,1]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        self.assertIs(principal0, principal1)

    def test_second(self):
        results = []
        def editor_append_second(point, path, resultsUnused, second):
            results.append([point, second] + path)

        principal = ('alpha', 'bravo', 'charlie')
        second = ('delta', 'echo', 'foxtrot')
        expected = [[value, second[index], index
                     ] for index, value in enumerate(principal)]
        del results[:]
        pathstore.walk(principal, editor_append_second, second=second)
        self.assertEqual(results, expected)

        class Instance:
            attr = 'Instance.attribute'
            attrOther = 'Instance.other attribute'
        
        principal = {'attr': 'dictionary attribute'}
        second = Instance()
        expected = [['dictionary attribute', 'Instance.attribute', 'attr']]
        del results[:]
        pathstore.walk(principal, editor_append_second, second=second)
        self.assertEqual(results, expected)

        principal = ('alpha', 'bravo',
                     {'attrOther': 'dictionary other attribute'}, 'charlie')
        second = ('delta', 'echo', Instance(), 'foxtrot')
        expected = [
            ['alpha', 'delta', 0],
            ['bravo', 'echo', 1],
            ['dictionary other attribute',
             'Instance.other attribute',
             2, 'attrOther'],
            ['charlie', 'foxtrot', 3]]
        del results[:]
        pathstore.walk(principal, editor_append_second, second=second)
        self.assertEqual(results, expected)

    def test_second_return(self):
        def editor_set(point, path, results, second):
            return True, second
        generic = {"a": None}
        aValue = {"c":"d"}
        principal = {"a":aValue}
        pathstore.walk(generic, editor_set, ["a"], second=principal)
        self.assertIs(generic['a'], aValue)
