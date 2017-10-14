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

class TestWalk(unittest.TestCase):    
    def test_noop_editor(self):
        principal = 23.4

        # Nothing but a pass, implicit return of None.
        def editor_pass(parent, path):
            pass
        walks = pathstore.walk(principal, editor_pass)
        self.assertEqual(walks, [])
        self.assertEqual(principal, 23.4)

        # Void return, also implicit return of None.
        def editor_void(parent, path):
            return
        walks = pathstore.walk(principal, editor_void)
        self.assertEqual(walks, [])
        self.assertEqual(principal, 23.4)

        def editor_none(parent, path):
            return None
        walks = pathstore.walk(principal, editor_none)
        self.assertEqual(walks, [])
        self.assertEqual(principal, 23.4)

        def editor_false(parent, path):
            return False
        walks = pathstore.walk(principal, editor_false)
        self.assertEqual(walks, [])
        self.assertEqual(principal, 23.4)

        def editor_true(parent, path):
            return True
        with self.assertRaises(TypeError) as context:
            walks = pathstore.walk(principal, editor_true)
        self.assertEqual(
            str(context.exception), "'bool' object is not subscriptable")
        self.assertEqual(principal, 23.4)

        def editor_single_false(parent, path):
            return [False]
        walks = pathstore.walk(principal, editor_false)
        self.assertEqual(walks, [])
        self.assertEqual(principal, 23.4)

        def editor_single_true(parent, path):
            return [True]
        with self.assertRaises(IndexError) as context:
            walks = pathstore.walk(principal, editor_single_true)
        self.assertEqual(
            str(context.exception), "list index out of range")
        self.assertEqual(principal, 23.4)

        unboundVariable = 20
        def editor_unbound(parent, path):
            unboundVariable += 2
        with self.assertRaises(UnboundLocalError) as context:
            walks = pathstore.walk(principal, editor_unbound)
        self.assertEqual(
            str(context.exception)
            , "local variable 'unboundVariable' referenced before assignment")
        self.assertEqual(principal, 23.4)

    def test_scalar(self):
        principal = 4
        def editor(parent, path):
            return True, [parent] + path
        
        walks = pathstore.walk(principal, editor)
        self.assertEqual(walks, [[4]])
        self.assertEqual(principal, 4)
        
        with self.assertRaises(TypeError) as context:
            walks = pathstore.walk(principal, editor, 0)
        self.assertEqual(
            str(context.exception), "Couldn't get point for 0 in 4")

    def test_list(self):
        principal = [2, 3]
        def editor(parent, path):
            return True, [parent] + path
        
        walks = pathstore.walk(tuple(), editor)
        self.assertEqual(walks, [])

        walks = pathstore.walk([], editor)
        self.assertEqual(walks, [])

        principal0 = principal[:]
        walks = pathstore.walk(principal0, editor)
        self.assertEqual(walks, [[2,0], [3,1]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        
        principal0 = principal[:]
        walks = pathstore.walk(principal0, editor, 1)
        self.assertEqual(walks, [[3,1]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)
        
        with self.assertRaises(IndexError) as context:
            walks = pathstore.walk(principal, editor, 2)
        self.assertEqual(
            str(context.exception), "No point for 2 in {}".format(principal))

    def test_list_nested(self):
        principal = ['d', ['a', 'b'], 'c']
        # Deep copy by pasting.
        principal0 = ['d', ['a', 'b'], 'c']
        def editor(parent, path):
            return True, [parent] + path
        
        walks = pathstore.walk(principal0, editor)

        self.assertEqual(walks, [
            ['d', 0], ['a', 1, 0], ['b', 1, 1], ['c', 2]])
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)

    def test_dict(self):
        principal = {'ef':'jape', 'gh': 'idol', 'kl': 'master'}
        principal0 = dict(principal)
        def editor(parent, path):
            return True, [parent] + path
        expectedWalks = [['idol', 'gh'], ['jape', 'ef'], ['master', 'kl']]
        expectedWalks.sort()
        
        walks = pathstore.walk(principal0, editor)
        walks.sort()

        self.assertEqual(walks, expectedWalks)
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)

        walks = pathstore.walk({}, editor)
        self.assertEqual(walks, [])

    def test_list_dict(self):
        principal = [{'ef':'jape', 'gh': 'idol', 'kl': 'master'}, {'no':'yes'}]
        principal0 = [{'ef':'jape', 'gh': 'idol', 'kl': 'master'}, {'no':'yes'}]
        def editor(parent, path):
            return True, [parent] + path
        expectedWalks = [
            ['idol', 0, 'gh'], ['jape', 0, 'ef'], ['master', 0, 'kl'],
            ['yes', 1, 'no']]
        expectedWalks.sort()
        
        walks = pathstore.walk(principal0, editor)
        walks.sort()

        self.assertEqual(walks, expectedWalks)
        self.assertEqual(principal0, principal)
        self.assertIsNot(principal0, principal)

    def test_list_object(self):
        mock0 = Mock(spec_set=['attr'])
        mock0.attr = 11
        mock1 = Mock(mock0)
        mock1.attr = 13
        principal = [mock0, mock1]

        def editor0(parent, path):
            parent.attr += 1
            return True, [parent] + path
        walks = pathstore.walk(principal, editor0)
        self.assertEqual(walks, [[mock0,0], [mock1,1]])
        self.assertEqual(mock0.attr, 12)
        self.assertEqual(mock1.attr, 14)

        def editor1(parent, path):
            if parent.attr < 14:
                return False, None
            parent.attr += 1
            return True, [parent] + path
        walks = pathstore.walk(principal, editor1)
        self.assertEqual(walks, [[mock1,1]])
        self.assertEqual(mock0.attr, 12)
        self.assertEqual(mock1.attr, 15)
