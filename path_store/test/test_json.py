#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestJSON
"""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for JavaScript Object Notation (JSON) strings.
# https://docs.python.org/3.5/library/json.html
import json
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
import path_store.pathstore
import path_store.rest

class SerialiseToNull(object):
    pass

class CannotSerialise(object):
    pass

class Encoder(json.JSONEncoder):
    def default(self, object_):
        if isinstance(object_, SerialiseToNull):
            return None
        return json.JSONEncoder.default(self, object_)

class TestJSON(unittest.TestCase):
    def test_mock(self):
        #
        # Working use of Mock: one instance wraps the method.
        encoder = Encoder()
        mockDefault = Mock(side_effect=encoder.default)
        encoder.default = mockDefault
        #
        # Dummy that will be called in the expected sequence.
        mockCorrect = Mock()
        #
        # Instance of a class that should be passed to Encoder.default().
        serialiseToNull = SerialiseToNull()
        mockCorrect(serialiseToNull)
        self.assertEqual(encoder.encode([4,3, serialiseToNull])
                         , json.dumps([4,3, None]))
        mockCorrect.assert_has_calls(mockDefault.mock_calls)
        #
        # The following use of Mock doesn't work. Wrapping an object doesn't
        # cause its methods to be tracked, certainly if called from other
        # methods in the object.
        mock = Mock(wraps=Encoder())
    
    def test_cannot_serialize(self):
        encoder = Encoder()
        with self.assertRaises(TypeError) as context:
            result = encoder.encode([7, "hi", CannotSerialise()])
