#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestDescend
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
# Utilities.
from . import principal
#
# Modules under test.
from hosted import HostedProperty

class Host(object):
    hostedTuple = None
    hostedList = None
    
    def __init__(self, tupleValue, listValue):
        self.hostedTuple = tuple(tupleValue)
        self.hostedList = listValue
        
class Principal(principal.Principal):
    @property
    def host(self):
        return self._host

    hostedTuple = HostedProperty('hostedTuple', 'host')
    hostedList = HostedProperty('hostedList', 'host')
    
    def __init__(self, tupleValue, listValue, value=None):
        self.hostedTuple = None
        self.hostedList = None
        self._host = Host(tupleValue, listValue)
        super().__init__(value)

class TestHostedProperty(unittest.TestCase):
    def test_host(self):
        host = Host([0], [1])
        self.assertEqual(host.hostedTuple, (0,))
        self.assertIsInstance(host.hostedTuple, tuple)
        self.assertEqual(host.hostedList, [1])
        self.assertIsInstance(host.hostedList, list)
        
    def test_hosted_setter(self):
        tuple0 = (1,2)
        self.assertIs(tuple0, tuple(tuple0))
        self.assertIs(tuple0, tuple0.__class__(tuple0))
        
        list0 = [3,4]
        self.assertIsNot(list0, list(list0))
        self.assertIsNot(list0, list0.__class__(list0))

        principal = Principal(tuple0, list0)
        self.assertIs(principal.host.hostedTuple, tuple0)
        self.assertIs(principal.host.hostedList.__class__, list0.__class__)
        self.assertIs(principal.host.hostedList, list0)
        
        tuple1 = (5,6)
        hosted = principal.hostedTuple
        principal.hostedTuple = tuple1
        #
        # Check that the Holder object persists through the set.
        self.assertIs(principal.hostedTuple, hosted)
        self.assertIs(principal.host.hostedTuple, tuple1)
        self.assertIsNot(principal.host.hostedTuple, tuple0)
        
        list1 = [7,8]
        hosted = principal.hostedList
        principal.hostedList = list1
        self.assertIs(principal.hostedList, hosted)
        self.assertIs(principal.host.hostedList, list1)
        self.assertIsNot(principal.host.hostedList, list0)
        
        hosted = principal.hostedList
        principal.hostedList = tuple1
        self.assertIs(principal.hostedList, hosted)
        self.assertEqual(principal.host.hostedList, list(tuple1))
        self.assertIsInstance(tuple1, tuple)
        self.assertIsInstance(principal.host.hostedList, list)
        
        
    def test_tuple_holder_setter(self):
        principal = Principal([1,2], tuple())
        hostedTuple0 = principal.hostedTuple
        nativeTuple0 = principal.host.hostedTuple
        self.assertEqual([1,2], list(principal.hostedTuple[:]))

        principal.hostedTuple[1] = 3
        #
        # The underlying property must change, because it is a tuple and
        # therefore immutable.
        self.assertIsNot(nativeTuple0, principal.host.hostedTuple)
        nativeTuple0 = principal.host.hostedTuple
        self.assertIs(hostedTuple0, principal.hostedTuple)
        self.assertEqual([1,3], list(principal.hostedTuple[:]))
        
        principal.hostedTuple[2:2] = (4,)
        self.assertIsNot(nativeTuple0, principal.host.hostedTuple)
        nativeTuple0 = principal.host.hostedTuple
        self.assertIs(hostedTuple0, principal.hostedTuple)
        self.assertEqual([1,3,4], list(principal.hostedTuple[:]))
        
        principal.hostedTuple[0:1] = (5, 6, 7)
        self.assertIsNot(nativeTuple0, principal.host.hostedTuple)
        nativeTuple0 = principal.host.hostedTuple
        self.assertIs(hostedTuple0, principal.hostedTuple)
        self.assertEqual([5,6,7,3,4], list(principal.hostedTuple[:]))
        
        del principal.hostedTuple[1]
        self.assertIsNot(nativeTuple0, principal.host.hostedTuple)
        nativeTuple0 = principal.host.hostedTuple
        self.assertIs(hostedTuple0, principal.hostedTuple)
        self.assertEqual([5,7,3,4], list(principal.hostedTuple[:]))

