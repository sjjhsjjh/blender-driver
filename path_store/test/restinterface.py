#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestRestInterface
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
from path_store import rest
from path_store.blender_game_engine import gameobjectcollection

class MockGameObject(Mock):
    def endObject(self):
        pass

class TestRestInterface(unittest.TestCase):
    
    def test_gameobjectlist(self):
        mock = MockGameObject()
        mock.endObject = Mock()
        interface = rest.AnimatedRestInterface()
        
        # Test that a collection of the required type was inserted and
        # populated with None placeholders.
        interface.rest_put(mock, interface.gameObjectPath + (2,))
        self.assertIsInstance(interface.rest_get(interface.gameObjectPath)
                              , gameobjectcollection.GameObjectList)
        self.assertIsNone(interface.rest_get(interface.gameObjectPath + (0,)))
        self.assertIsNone(interface.rest_get(interface.gameObjectPath + (1,)))
        self.assertIs(
            mock, interface.rest_get(interface.gameObjectPath + (2,)))
        self.assertEqual(3, len(interface.rest_get(interface.gameObjectPath)))
        self.assertEqual(0, len(mock.endObject.call_args_list))

        # Test that deleting the mock element, which is last, results in a call
        # to its endObject method, and it gets deleted. 
        del interface.rest_get(interface.gameObjectPath)[-1]
        self.assertEqual(
            interface.rest_get(interface.gameObjectPath), [None, None])
        self.assertEqual(mock.endObject.call_args_list, [call()])
        #
        # Test that deleting a different element also works.
        del interface.rest_get(interface.gameObjectPath)[0]
        self.assertEqual(
            interface.rest_get(interface.gameObjectPath), [None])
        #
        # Test deleting with the rest interface, which returns the deleted
        # object.
        mock.reset_mock()
        mock.endObject.reset_mock()
        #
        # First put the object back.
        interface.rest_put(mock, interface.gameObjectPath + (3,))
        #
        # Next line failed at first, because isinstance(UserList instance, list)
        # is False. Subsequently fixed though.
        self.assertEqual(4, len(interface.rest_get(interface.gameObjectPath))
                         , interface.rest_get(interface.gameObjectPath))
        self.assertIsNone(interface.rest_get(interface.gameObjectPath + (0,)))
        self.assertIsNone(interface.rest_get(interface.gameObjectPath + (1,)))
        self.assertIsNone(interface.rest_get(interface.gameObjectPath + (2,)))
        self.assertIs(
            mock, interface.rest_get(interface.gameObjectPath + (3,)))
        self.assertEqual(0, len(mock.endObject.call_args_list))
        #
        # Actual interface usage here.
        deleted = interface.rest_delete(interface.gameObjectPath + (3,))
        self.assertIs(mock, deleted)
        self.assertEqual(
            interface.rest_get(interface.gameObjectPath), [None, None, None])
        self.assertEqual(mock.endObject.call_args_list, [call()])
