#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestHostedProperty
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
import path_store.test.principal
#
# Modules under test.
from path_store.hosted import HostedProperty

class ReadOnly(list):
    """Class with same behaviour as the KX_GameObject.worldScale property:
    Has __setitem__ and __delitem__ but is read only, so raises an error when
    either is called.
    """
    def __setitem__(self, specifier, value):
        raise AttributeError("ReadOnly __setitem__ called.")

    def __delitem__(self, specifier):
        raise TypeError("ReadOnly __delitem__ called.")

class Host(object):
    hostedTuple = None
    hostedList = None
    hostedReadOnly = None
    
    def __init__(self, tupleValue, listValue, readOnlyValue):
        self.hostedTuple = tuple(tupleValue)
        self.hostedList = listValue
        self.hostedReadOnly = readOnlyValue
        
class Principal(path_store.test.principal.Principal):
    @property
    def host(self):
        return self._host

    hostedTuple = HostedProperty('hostedTuple', 'host')
    hostedList = HostedProperty('hostedList', 'host')
    hostedReadOnly = HostedProperty('hostedReadOnly', 'host')
    
    def __init__(self, tupleValue, listValue, readOnlyValue, value=None):
        self.hostedTuple = None
        self.hostedList = None
        self.hostedReadOnly = None
        self._host = Host(tupleValue, listValue, readOnlyValue)
        super().__init__(value)

class TestHostedProperty(unittest.TestCase):
    def test_host(self):
        tuple_ = (0,)
        list_ = [1]
        readonly = ReadOnly([2])
        host = Host(tuple_, list_, readonly)
        self.assertIs(host.hostedTuple, tuple_)
        self.assertIs(host.hostedList, list_)
        self.assertIs(host.hostedReadOnly, readonly)
        
    def test_hosted_setter(self):
        tuple0 = (1,2)
        self.assertIs(tuple0, tuple(tuple0))
        self.assertIs(tuple0, tuple0.__class__(tuple0))
        
        list0 = [3,4]
        self.assertIsNot(list0, list(list0))
        self.assertIsNot(list0, list0.__class__(list0))

        principal = Principal(tuple0, list0, tuple())
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
        
    def test_tuple_holder_setitem(self):
        principal = Principal([1,2], tuple(), tuple())
        hosted = principal.hostedTuple
        underlaying = principal.host.hostedTuple
        self.assertEqual([1,2], list(principal.hostedTuple[:]))

        principal.hostedTuple[1] = 3
        #
        # In all cases, the underlying property must change, because it is a
        # tuple and therefore immutable, hence assertIsNot.
        self.assertIsNot(underlaying, principal.host.hostedTuple)
        underlaying = principal.host.hostedTuple
        self.assertIs(hosted, principal.hostedTuple)
        self.assertEqual([1,3], list(principal.hostedTuple[:]))
        
        principal.hostedTuple[2:2] = (4,)
        self.assertIsNot(underlaying, principal.host.hostedTuple)
        underlaying = principal.host.hostedTuple
        self.assertIs(hosted, principal.hostedTuple)
        self.assertEqual([1,3,4], list(principal.hostedTuple[:]))
        
        principal.hostedTuple[0:1] = (5, 6, 7)
        self.assertIsNot(underlaying, principal.host.hostedTuple)
        underlaying = principal.host.hostedTuple
        self.assertIs(hosted, principal.hostedTuple)
        self.assertEqual([5,6,7,3,4], list(principal.hostedTuple[:]))
        
        del principal.hostedTuple[1]
        self.assertIsNot(underlaying, principal.host.hostedTuple)
        underlaying = principal.host.hostedTuple
        self.assertIs(hosted, principal.hostedTuple)
        self.assertEqual([5,7,3,4], list(principal.hostedTuple[:]))

    def test_readonly_holder_setitem(self):
        principal = Principal(tuple(), tuple(), ReadOnly([1,2]))
        hosted = principal.hostedReadOnly
        underlaying = principal.host.hostedReadOnly
        self.assertEqual([1,2], list(principal.hostedReadOnly[:]))

        principal.hostedReadOnly[1] = 3
        #
        # In all cases, the underlying property must change, because it is
        # immutable, hence assertIsNot.
        self.assertIsNot(underlaying, principal.host.hostedReadOnly)
        underlaying = principal.host.hostedReadOnly
        self.assertIs(hosted, principal.hostedReadOnly)
        self.assertEqual([1,3], principal.hostedReadOnly[:])
        
        principal.hostedReadOnly[2:2] = (4,)
        self.assertIsNot(underlaying, principal.host.hostedReadOnly)
        underlaying = principal.host.hostedReadOnly
        self.assertIs(hosted, principal.hostedReadOnly)
        self.assertEqual([1,3,4], principal.hostedReadOnly[:])
        
        principal.hostedReadOnly[0:1] = (5, 6, 7)
        self.assertIsNot(underlaying, principal.host.hostedReadOnly)
        underlaying = principal.host.hostedReadOnly
        self.assertIs(hosted, principal.hostedReadOnly)
        self.assertEqual([5,6,7,3,4], principal.hostedReadOnly[:])
        
        del principal.hostedReadOnly[1]
        self.assertIsNot(underlaying, principal.host.hostedReadOnly)
        underlaying = principal.host.hostedReadOnly
        self.assertIs(hosted, principal.hostedReadOnly)
        self.assertEqual([5,7,3,4], principal.hostedReadOnly[:])

    def test_list_holder_setitem(self):
        list_ = [1,2]
        principal = Principal(tuple(), list_, tuple())
        hosted = principal.hostedList
        underlaying = principal.host.hostedList
        self.assertEqual(list_, hosted[:])
        self.assertIs(list_, underlaying)

        principal.hostedList[1] = 3
        #
        # The underlying property shouldn't change, because it is mutable.
        self.assertIs(underlaying, principal.host.hostedList)
        self.assertIs(hosted, principal.hostedList)
        self.assertIs(list_, underlaying)
        self.assertEqual([1,3], list_)
        
        principal.hostedList[2:2] = [4]
        self.assertIs(underlaying, principal.host.hostedList)
        self.assertIs(hosted, principal.hostedList)
        self.assertIs(list_, underlaying)
        self.assertEqual([1,3,4], list_)
        
        principal.hostedList[0:1] = (5, 6, 7)
        self.assertIs(underlaying, principal.host.hostedList)
        self.assertIs(hosted, principal.hostedList)
        self.assertIs(list_, underlaying)
        self.assertEqual([5,6,7,3,4], list_)
        
        del principal.hostedList[1]
        self.assertIs(underlaying, principal.host.hostedList)
        self.assertIs(hosted, principal.hostedList)
        self.assertIs(list_, underlaying)
        self.assertEqual([5,7,3,4], list_)

    def test_list_holder_getitem(self):
        listItem1 = [None]
        list_ = [1,listItem1]
        principal = Principal(tuple(), list_, tuple())
        self.assertEqual(1, principal.hostedList[0])
        self.assertIs(listItem1, principal.hostedList[1])

    def test_holder_method(self):
        principal = Principal([1,2], tuple(), tuple())
        hosted = principal.hostedTuple
        self.assertEqual(2, len(hosted))
        self.assertEqual(1, hosted.count(2))
