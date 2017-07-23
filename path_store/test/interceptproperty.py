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
from hosted import InterceptProperty, InterceptCast

class ReadOnly(list):
    """Class with same behaviour as the KX_GameObject.worldScale property:
    Has __setitem__ and __delitem__ but is read only, so raises an error when
    either is called.
    """
    def __setitem__(self, specifier, value):
        raise AttributeError("ReadOnly __setitem__ called.")

    def __delitem__(self, specifier):
        raise TypeError("ReadOnly __delitem__ called.")

class Destination(object):
    destinationTuple = None
    destinationList = None
    destinationReadOnly = None
    
    def __init__(self, tupleValue, listValue, readOnlyValue):
        self.destinationTuple = tuple(tupleValue)
        self.destinationList = listValue
        self.destinationReadOnly = readOnlyValue
        
class Principal(principal.Principal):
    """Subclass of Principal that uses InterceptProperty to access properties of
    an object that is itself a property, like a sub-property.
    """
    @property
    def destination(self):
        return self._destination
    
    @InterceptProperty(InterceptCast.IFDIFFERENTTHEN)
    def destinationTuple(self):
        return self.destination.destinationTuple
    @destinationTuple.intercept_getter
    def destinationTuple(self):
        return self._destinationTuple
    @destinationTuple.intercept_setter
    def destinationTuple(self, value):
        self._destinationTuple = value
    @destinationTuple.destination_setter
    def destinationTuple(self, value):
        self.destination.destinationTuple = value

    @InterceptProperty(InterceptCast.IFDIFFERENTNOW)
    def destinationList(self):
        return self.destination.destinationList
    @destinationList.intercept_getter
    def destinationList(self):
        return self._destinationList
    @destinationList.intercept_setter
    def destinationList(self, value):
        self._destinationList = value
    @destinationList.destination_setter
    def destinationList(self, value):
        self.destination.destinationList = value

    @InterceptProperty(InterceptCast.IFDIFFERENTTHEN)
    def destinationReadOnly(self):
        return self.destination.destinationReadOnly
    @destinationReadOnly.intercept_getter
    def destinationReadOnly(self):
        return self._destinationReadOnly
    @destinationReadOnly.intercept_setter
    def destinationReadOnly(self, value):
        self._destinationReadOnly = value
    @destinationReadOnly.destination_setter
    def destinationReadOnly(self, value):
        self.destination.destinationReadOnly = value

    def __init__(self, tupleValue, listValue, readOnlyValue, value=None):
        self._destination = Destination(tupleValue, listValue, readOnlyValue)
        super().__init__(value)

class Base(object):
    @property
    def destinationTuple(self):
        return self._destinationTuple
    @destinationTuple.setter
    def destinationTuple(self, value):
        self._destinationTuple = value
    
    @property
    def destinationList(self):
        return self._destinationList
    @destinationList.setter
    def destinationList(self, value):
        self._destinationList = value
    
    @property
    def destinationReadOnly(self):
        return self._destinationReadOnly
    @destinationReadOnly.setter
    def destinationReadOnly(self, value):
        self._destinationReadOnly = value
        
    @property
    def destinationStr(self):
        return self._destinationStr
    @destinationStr.setter
    def destinationStr(self, value):
        self._destinationStr = value
    
    def __init__(self, tupleValue, listValue, readOnlyValue, strValue):
        self._destinationTuple = tuple(tupleValue)
        self._destinationList = listValue
        self._destinationReadOnly = readOnlyValue
        self._destinationStr = strValue
        
class InterceptSuper(Base):
    """Subclass of Base that uses InterceptProperty with super() in its
    intercept setter and getter. It also has properties that bypass the
    intercept.
    
    This class has to use internal properties with different names than the base
    class internal property names.
    """
    @InterceptProperty(InterceptCast.IFDIFFERENTTHEN)
    def destinationTuple(self):
        return super().destinationTuple
    @destinationTuple.intercept_getter
    def destinationTuple(self):
        return self._destinationTupleIntercept
    @destinationTuple.intercept_setter
    def destinationTuple(self, value):
        self._destinationTupleIntercept = value
    @destinationTuple.destination_setter
    def destinationTuple(self, value):
        # It'd be nice to do this:
        #
        #     super(self).destinationTuple = value
        #
        # But see this issue: http://bugs.python.org/issue14965
        # So instead, we have the following.
        super(self.__class__, self.__class__
              ).destinationTuple.__set__(self, value)
        #
        # The following would also work and wouldn't incur instantiation of a
        # super object.
        # Base.destinationTuple.__set__(self, value)
        
    @InterceptProperty(InterceptCast.IFDIFFERENTTHEN)
    def destinationList(self):
        return super().destinationList
    @destinationList.intercept_getter
    def destinationList(self):
        return self._destinationListIntercept
    @destinationList.intercept_setter
    def destinationList(self, value):
        self._destinationListIntercept = value
    @destinationList.destination_setter
    def destinationList(self, value):
        Base.destinationList.__set__(self, value)

    @InterceptProperty(InterceptCast.IFDIFFERENTTHEN)
    def destinationReadOnly(self):
        return super().destinationReadOnly
    @destinationReadOnly.intercept_getter
    def destinationReadOnly(self):
        return self._destinationReadOnlyIntercept
    @destinationReadOnly.intercept_setter
    def destinationReadOnly(self, value):
        self._destinationReadOnlyIntercept = value
    @destinationReadOnly.destination_setter
    def destinationReadOnly(self, value):
        Base.destinationReadOnly.__set__(self, value)

    # Properties for access to base properties without interception, for testing
    # only.
    @property
    def baseTuple(self):
        return super().destinationTuple
    @property
    def baseList(self):
        return super().destinationList
    @property
    def baseReadOnly(self):
        return super().destinationReadOnly

class InterceptAlternative(Base):
    """Subclass of Base that uses InterceptProperty with different property
    names. The name have Items appended as a reminder that the main reason for
    interception is to make accessible the items.
    
    This class uses conventionally named internal properties.
    """
    @InterceptProperty(InterceptCast.IFDIFFERENTTHEN)
    def destinationTupleItems(self):
        return self.destinationTuple
    @destinationTupleItems.intercept_getter
    def destinationTupleItems(self):
        return self._destinationTupleItems
    @destinationTupleItems.intercept_setter
    def destinationTupleItems(self, value):
        self._destinationTupleItems = value
    @destinationTupleItems.destination_setter
    def destinationTupleItems(self, value):
        self.destinationTuple = value
 
    @InterceptProperty(InterceptCast.IFDIFFERENTTHEN)
    def destinationListItems(self):
        return self.destinationList
    @destinationListItems.intercept_getter
    def destinationListItems(self):
        return self._destinationListItems
    @destinationListItems.intercept_setter
    def destinationListItems(self, value):
        self._destinationListItems = value
    @destinationListItems.destination_setter
    def destinationListItems(self, value):
        self.destinationList = value
 
    @InterceptProperty(InterceptCast.IFDIFFERENTTHEN)
    def destinationReadOnlyItems(self):
        return self.destinationReadOnly
    @destinationReadOnlyItems.intercept_getter
    def destinationReadOnlyItems(self):
        return self._destinationReadOnlyItems
    @destinationReadOnlyItems.intercept_setter
    def destinationReadOnlyItems(self, value):
        self._destinationReadOnlyItems = value
    @destinationReadOnlyItems.destination_setter
    def destinationReadOnlyItems(self, value):
        self.destinationReadOnly = value

class InterceptCastOptions(Base):
    @InterceptProperty(InterceptCast.NONE)
    def destinationStrCastNo(self):
        return self.destinationStr
    @destinationStrCastNo.intercept_getter
    def destinationStrCastNo(self):
        return self._destinationStrCastNo
    @destinationStrCastNo.intercept_setter
    def destinationStrCastNo(self, value):
        self._destinationStrCastNo = value
    @destinationStrCastNo.destination_setter
    def destinationStrCastNo(self, value):
        self.destinationStr = value


    
 
class TestInterceptProperty(unittest.TestCase):
    def test_destination_class(self):
        tuple_ = (0,)
        list_ = [1]
        readonly = ReadOnly([2])
        destination = Destination(tuple_, list_, readonly)
        self.assertIs(destination.destinationTuple, tuple_)
        self.assertIs(destination.destinationList, list_)
        self.assertIs(destination.destinationReadOnly, readonly)
        
    def test_destination_setter(self):
        tuple0 = (1,2)
        self.assertIs(tuple0, tuple(tuple0))
        self.assertIs(tuple0, tuple0.__class__(tuple0))
        
        list0 = [3,4]
        self.assertIsNot(list0, list(list0))
        self.assertIsNot(list0, list0.__class__(list0))

        principal = Principal(tuple0, list0, tuple())
        self.assertIs(principal.destination.destinationTuple, tuple0)
        self.assertIs(principal.destination.destinationList.__class__
                      , list0.__class__)
        self.assertIs(principal.destination.destinationList, list0)
        
        tuple1 = (5,6)
        destination = principal.destinationTuple
        principal.destinationTuple = tuple1
        #
        # Check that the Holder object persists through the set.
        self.assertIs(principal.destinationTuple, destination)
        self.assertIs(principal.destination.destinationTuple, tuple1)
        self.assertIsNot(principal.destination.destinationTuple, tuple0)
        
        list1 = [7,8]
        destination = principal.destinationList
        principal.destinationList = list1
        self.assertIs(principal.destinationList, destination)
        self.assertIs(principal.destination.destinationList, list1)
        self.assertIsNot(principal.destination.destinationList, list0)
        
        destination = principal.destinationList
        principal.destinationList = tuple1
        # Getting principal.destinationList returns the holder, which doesn't
        # change.
        self.assertIs(principal.destinationList, destination)
        self.assertEqual(principal.destination.destinationList, list(tuple1))
        self.assertIsInstance(tuple1, tuple)
        self.assertIsInstance(principal.destination.destinationList, list)
        
    def test_tuple_destination_setitem(self):
        principal = Principal([1,2], tuple(), tuple())
        intercept = principal.destinationTuple
        underlaying = principal.destination.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertEqual((1,2), principal.destinationTuple[:])
    
        principal.destinationTuple[1] = 3
        #
        # In all cases, the underlying property must change, because it is a
        # tuple and therefore immutable, hence assertIsNot.
        self.assertIsNot(underlaying, principal.destination.destinationTuple)
        underlaying = principal.destination.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        #
        # The intercept variable is a reference to the holder, so it doesn't
        # change in any case, hence assertIs.
        self.assertIs(intercept, principal.destinationTuple)
        self.assertEqual([1,3], list(principal.destinationTuple[:]))
        
        principal.destinationTuple[2:2] = (4,)
        self.assertIsNot(underlaying, principal.destination.destinationTuple)
        underlaying = principal.destination.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(intercept, principal.destinationTuple)
        self.assertEqual([1,3,4], list(principal.destinationTuple[:]))
        
        principal.destinationTuple[0:1] = (5, 6, 7)
        self.assertIsNot(underlaying, principal.destination.destinationTuple)
        underlaying = principal.destination.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(intercept, principal.destinationTuple)
        self.assertEqual([5,6,7,3,4], list(principal.destinationTuple[:]))
        
        del principal.destinationTuple[1]
        self.assertIsNot(underlaying, principal.destination.destinationTuple)
        underlaying = principal.destination.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(intercept, principal.destinationTuple)
        self.assertEqual([5,7,3,4], list(principal.destinationTuple[:]))
    
    def test_readonly_destination_setitem(self):
        principal = Principal(tuple(), tuple(), ReadOnly([1,2]))
        intercept = principal.destinationReadOnly
        underlaying = principal.destination.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertEqual([1,2], principal.destinationReadOnly[:])
    
        principal.destinationReadOnly[1] = 3
        #
        # In all cases, the underlying property must change, because it is
        # immutable, hence assertIsNot.
        self.assertIsNot(underlaying, principal.destination.destinationReadOnly)
        underlaying = principal.destination.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(intercept, principal.destinationReadOnly)
        self.assertEqual([1,3], principal.destinationReadOnly[:])
        
        principal.destinationReadOnly[2:2] = (4,)
        self.assertIsNot(underlaying, principal.destination.destinationReadOnly)
        underlaying = principal.destination.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(intercept, principal.destinationReadOnly)
        self.assertEqual([1,3,4], principal.destinationReadOnly[:])
        
        principal.destinationReadOnly[0:1] = (5, 6, 7)
        self.assertIsNot(underlaying, principal.destination.destinationReadOnly)
        underlaying = principal.destination.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(intercept, principal.destinationReadOnly)
        self.assertEqual([5,6,7,3,4], principal.destinationReadOnly[:])
        
        del principal.destinationReadOnly[1]
        self.assertIsNot(underlaying, principal.destination.destinationReadOnly)
        underlaying = principal.destination.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(intercept, principal.destinationReadOnly)
        self.assertEqual([5,7,3,4], principal.destinationReadOnly[:])
    
    def test_list_destination_setitem(self):
        list_ = [1,2]
        principal = Principal(tuple(), list_, tuple())
        intercept = principal.destinationList
        underlaying = principal.destination.destinationList
        self.assertEqual(list_, intercept[:])
        self.assertIs(list_, underlaying)
    
        principal.destinationList[1] = 3
        #
        # The underlying property shouldn't change, because it is mutable.
        self.assertIs(underlaying, principal.destination.destinationList)
        self.assertIs(intercept, principal.destinationList)
        self.assertIs(list_, underlaying)
        self.assertEqual([1,3], list_)
        
        principal.destinationList[2:2] = [4]
        self.assertIs(underlaying, principal.destination.destinationList)
        self.assertIs(intercept, principal.destinationList)
        self.assertIs(list_, underlaying)
        self.assertEqual([1,3,4], list_)
        
        principal.destinationList[0:1] = (5, 6, 7)
        self.assertIs(underlaying, principal.destination.destinationList)
        self.assertIs(intercept, principal.destinationList)
        self.assertIs(list_, underlaying)
        self.assertEqual([5,6,7,3,4], list_)
        
        del principal.destinationList[1]
        self.assertIs(underlaying, principal.destination.destinationList)
        self.assertIs(intercept, principal.destinationList)
        self.assertIs(list_, underlaying)
        self.assertEqual([5,7,3,4], list_)
    
    def test_list_destination_getitem(self):
        listItem1 = [None]
        list_ = [1, listItem1]
        principal = Principal(tuple(), list_, tuple())
        self.assertEqual(1, principal.destinationList[0])
        self.assertIs(listItem1, principal.destinationList[1])
    
    def test_destination_property_method(self):
        principal = Principal([1,2], tuple(), tuple())
        intercept = principal.destinationTuple
        self.assertEqual(2, len(intercept))
        self.assertEqual(1, intercept.count(2))

    def test_base_class(self):
        tuple_ = (0,)
        list_ = [1]
        readonly = ReadOnly([2])
        str_ = "three"
        base = Base(tuple_, list_, readonly, str_)
        self.assertIs(base.destinationTuple, tuple_)
        self.assertIs(base.destinationList, list_)
        self.assertIs(base.destinationReadOnly, readonly)
        self.assertIs(base.destinationStr, str_)
        
    def test_intercept_super_class(self):
        tuple_ = (0,)
        list_ = [1]
        readonly = ReadOnly([2])
        intercept = InterceptSuper(tuple_, list_, readonly, "three")
        self.assertIs(intercept.baseTuple, tuple_)
        self.assertIs(intercept.baseList, list_)
        self.assertIs(intercept.baseReadOnly, readonly)
        
    def test_super_setter(self):
        tuple0 = (1,2)
        list0 = [3,4]
        intercept = InterceptSuper(tuple0, list0, tuple(), "three")
        self.assertIsNot(intercept.destinationTuple, tuple0)
        self.assertEqual(intercept.destinationTuple[:], tuple0)
        self.assertIs(intercept.baseTuple, tuple0)
        self.assertIsNot(intercept.destinationList.__class__, list0.__class__)
        self.assertEqual(intercept.destinationList[:], list0)
        
        tuple1 = (5,6)
        propertyInstance = intercept.destinationTuple
        intercept.destinationTuple = tuple1
        #
        # Check that the Holder object persists through the set.
        self.assertIs(intercept.destinationTuple, propertyInstance)
        self.assertEqual(intercept.destinationTuple[:], tuple1)
        self.assertIs(intercept.baseTuple, tuple1)
        self.assertIsNot(intercept.destinationTuple, tuple0)
        
        list1 = [7,8]
        propertyInstance = intercept.destinationList
        intercept.destinationList = list1
        self.assertIs(intercept.destinationList, propertyInstance)
        self.assertEqual(intercept.destinationList[:], list1)
        self.assertIs(intercept.baseList, list1)
        self.assertIsNot(intercept.destinationList, list0)
        
        propertyInstance = intercept.destinationList
        intercept.destinationList = tuple1
        # Getting intercept.destinationList returns the holder, which doesn't
        # change.
        self.assertIs(intercept.destinationList, propertyInstance)
        self.assertEqual(intercept.destinationList[:], list(tuple1))
        self.assertIsInstance(tuple1, tuple)
        self.assertIsInstance(intercept.baseList, list)
        
    def test_tuple_super_setitem(self):
        intercept = InterceptSuper([1,2], tuple(), tuple(), "three")
        propertyInstance = intercept.destinationTuple
        underlaying = intercept.baseTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertEqual((1,2), intercept.destinationTuple[:])
    
        intercept.destinationTuple[1] = 3
        #
        # In all cases, the underlying property must change, because it is a
        # tuple and therefore immutable, hence assertIsNot.
        self.assertIsNot(underlaying, intercept.baseTuple)
        underlaying = intercept.baseTuple
        self.assertIsInstance(underlaying, tuple)
        #
        # The propertyInstance variable is a reference to the holder, so it doesn't
        # change in any case, hence assertIs.
        self.assertIs(propertyInstance, intercept.destinationTuple)
        self.assertEqual((1,3), intercept.destinationTuple[:])
        
        intercept.destinationTuple[2:2] = (4,)
        self.assertIsNot(underlaying, intercept.baseTuple)
        underlaying = intercept.baseTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(propertyInstance, intercept.destinationTuple)
        self.assertEqual((1,3,4), intercept.destinationTuple[:])
        
        intercept.destinationTuple[0:1] = (5, 6, 7)
        self.assertIsNot(underlaying, intercept.baseTuple)
        underlaying = intercept.baseTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(propertyInstance, intercept.destinationTuple)
        self.assertEqual((5,6,7,3,4), intercept.destinationTuple[:])
        
        del intercept.destinationTuple[1]
        self.assertIsNot(underlaying, intercept.baseTuple)
        underlaying = intercept.baseTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(propertyInstance, intercept.destinationTuple)
        self.assertEqual((5,7,3,4), intercept.destinationTuple[:])
    
    def test_readonly_super_setitem(self):
        intercept = InterceptSuper(tuple(), tuple(), ReadOnly([1,2]), "three")
        propertyInstance = intercept.destinationReadOnly
        underlaying = intercept.baseReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertEqual([1,2], intercept.destinationReadOnly[:])
    
        intercept.destinationReadOnly[1] = 3
        #
        # In all cases, the underlying property must change, because it is
        # immutable, hence assertIsNot.
        self.assertIsNot(underlaying, intercept.baseReadOnly)
        underlaying = intercept.baseReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        #
        # The propertyInstance variable is a reference to the holder, so it doesn't
        # change in any case, hence assertIs.
        self.assertIs(propertyInstance, intercept.destinationReadOnly)
        self.assertEqual([1,3], intercept.destinationReadOnly[:])
        
        intercept.destinationReadOnly[2:2] = (4,)
        self.assertIsNot(underlaying, intercept.baseReadOnly)
        underlaying = intercept.baseReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(propertyInstance, intercept.destinationReadOnly)
        self.assertEqual([1,3,4], intercept.destinationReadOnly[:])
        
        intercept.destinationReadOnly[0:1] = (5, 6, 7)
        self.assertIsNot(underlaying, intercept.baseReadOnly)
        underlaying = intercept.baseReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(propertyInstance, intercept.destinationReadOnly)
        self.assertEqual([5,6,7,3,4], intercept.destinationReadOnly[:])
        
        del intercept.destinationReadOnly[1]
        self.assertIsNot(underlaying, intercept.baseReadOnly)
        underlaying = intercept.baseReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(propertyInstance, intercept.destinationReadOnly)
        self.assertEqual([5,7,3,4], intercept.destinationReadOnly[:])
    
    def test_list_super_setitem(self):
        list_ = [1,2]
        intercept = InterceptSuper(tuple(), list_, tuple(), "three")
        propertyInstance = intercept.destinationList
        underlaying = intercept.baseList
        self.assertEqual(list_, propertyInstance[:])
        self.assertIs(list_, underlaying)
    
        intercept.destinationList[1] = 3
        #
        # The underlying property shouldn't change, because it is mutable.
        self.assertIs(underlaying, intercept.baseList)
        self.assertIs(propertyInstance, intercept.destinationList)
        self.assertIs(list_, underlaying)
        self.assertEqual([1,3], list_)
        
        intercept.destinationList[2:2] = [4]
        self.assertIs(underlaying, intercept.baseList)
        self.assertIs(propertyInstance, intercept.destinationList)
        self.assertIs(list_, underlaying)
        self.assertEqual([1,3,4], list_)
        
        intercept.destinationList[0:1] = (5, 6, 7)
        self.assertIs(underlaying, intercept.baseList)
        self.assertIs(propertyInstance, intercept.destinationList)
        self.assertIs(list_, underlaying)
        self.assertEqual([5,6,7,3,4], list_)
        
        del intercept.destinationList[1]
        self.assertIs(underlaying, intercept.baseList)
        self.assertIs(propertyInstance, intercept.destinationList)
        self.assertIs(list_, underlaying)
        self.assertEqual([5,7,3,4], list_)
    
    def test_list_super_getitem(self):
        listItem1 = [None]
        list_ = [1, listItem1]
        intercept = InterceptSuper(tuple(), list_, tuple(), "three")
        self.assertEqual(1, intercept.destinationList[0])
        self.assertIs(listItem1, intercept.destinationList[1])
        self.assertNotIsInstance(intercept.destinationList, list)
    
    def test_super_method(self):
        intercept = InterceptSuper([1,2], tuple(), tuple(), "three")
        self.assertEqual(2, len(intercept.destinationTuple))
        self.assertEqual(1, intercept.destinationTuple.count(2))

    def test_intercept_alternative_class(self):
        tuple_ = (0,)
        list_ = [1]
        readonly = ReadOnly([2])
        intercept = InterceptAlternative(tuple_, list_, readonly, "three")
        self.assertIs(intercept.destinationTuple, tuple_)
        self.assertIs(intercept.destinationList, list_)
        self.assertIs(intercept.destinationReadOnly, readonly)
        self.assertEqual(intercept.destinationTupleItems[:], tuple_)
        self.assertEqual(intercept.destinationListItems[:], list_)
        self.assertEqual(intercept.destinationReadOnlyItems[:], readonly)
        
    def test_alternative_setter(self):
        tuple0 = (1,2)
        list0 = [3,4]
        intercept = InterceptAlternative(tuple0, list0, tuple(), "three")
        self.assertIs(intercept.destinationTuple, tuple0)
        self.assertIsNot(intercept.destinationTupleItems, tuple0)
        self.assertEqual(intercept.destinationTupleItems[:], tuple0)
        self.assertIsNot(
            intercept.destinationTupleItems.__class__, tuple0.__class__)
        self.assertIs(intercept.destinationList, list0)
        self.assertIsNot(intercept.destinationListItems, list0)
        self.assertEqual(intercept.destinationListItems[:], list0)
        self.assertIsNot(
            intercept.destinationListItems.__class__, list0.__class__)
        
        tuple1 = (5,6)
        propertyInstance = intercept.destinationTupleItems
        intercept.destinationTupleItems = tuple1
        self.assertIs(intercept.destinationTuple, tuple1)
        self.assertIs(intercept.destinationTupleItems, propertyInstance)
        self.assertIsNot(intercept.destinationTuple, tuple0)
        self.assertEqual(intercept.destinationTupleItems[:], tuple1)
        
        list1 = [7,8]
        propertyInstance = intercept.destinationListItems
        intercept.destinationListItems = list1
        self.assertIs(intercept.destinationListItems, propertyInstance)
        self.assertEqual(intercept.destinationListItems[:], list1)
        self.assertIs(intercept.destinationList, list1)
        self.assertIsNot(intercept.destinationList, list0)
        self.assertIsNot(
            intercept.destinationList, intercept.destinationListItems)
        
        propertyInstance = intercept.destinationListItems
        intercept.destinationListItems = tuple1
        # Getting intercept.destinationList returns the holder, which doesn't
        # change.
        self.assertIs(intercept.destinationListItems, propertyInstance)
        self.assertEqual(intercept.destinationList[:], list(tuple1))
        self.assertEqual(intercept.destinationListItems[:], list(tuple1))
        self.assertIsInstance(tuple1, tuple)
        self.assertIsInstance(intercept.destinationList, list)
        
    def test_alternative_bypass_setter(self):
        tuple0 = (1,2)
        list0 = [3,4]
        intercept = InterceptAlternative(tuple0, list0, tuple(), "three")
        self.assertIs(intercept.destinationTuple, tuple0)
        self.assertIs(intercept.destinationList, list0)
        
        tuple1 = (5,6)
        propertyInstance = intercept.destinationTupleItems
        bypassInstance = intercept.destinationTuple
        intercept.destinationTuple = tuple1
        self.assertIs(intercept.destinationTuple, tuple1)
        self.assertIsNot(intercept.destinationTuple, bypassInstance)
        self.assertIs(intercept.destinationTupleItems, propertyInstance)
        self.assertEqual(intercept.destinationTupleItems[:], tuple1)

        list1 = [7,8]
        propertyInstance = intercept.destinationListItems
        bypassInstance = intercept.destinationList
        intercept.destinationList = list1
        self.assertIs(intercept.destinationList, list1)
        self.assertIsNot(intercept.destinationList, list0)
        self.assertIsNot(intercept.destinationList, bypassInstance)
        self.assertIs(intercept.destinationListItems, propertyInstance)
        self.assertEqual(intercept.destinationListItems[:], list1)
        
        propertyInstance = intercept.destinationListItems
        bypassInstance = intercept.destinationList
        intercept.destinationList = tuple1
        self.assertIs(intercept.destinationList, tuple1)
        self.assertIs(intercept.destinationListItems, propertyInstance)
        self.assertIsNot(intercept.destinationList, bypassInstance)
        self.assertIsInstance(tuple1, tuple)
        self.assertEqual(intercept.destinationListItems[:], tuple1)
        
    def test_tuple_alternative_setitem(self):
        intercept = InterceptAlternative([1,2], tuple(), tuple(), "three")
        propertyInstance = intercept.destinationTupleItems
        underlaying = intercept.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertEqual((1,2), intercept.destinationTuple[:])

        tuple_ = tuple((9,10))
        expected = None
        try:
            tuple_[0] = 11
        except TypeError as error:
            expected = error
        with self.assertRaises(TypeError) as context:
            intercept.destinationTuple[1] = 3
        self.assertEqual(str(context.exception), str(expected))

        intercept.destinationTupleItems[1] = 3
        #
        # In all cases, the underlying property must change, because it is a
        # tuple and therefore immutable, hence assertIsNot.
        self.assertIsNot(underlaying, intercept.destinationTuple)
        underlaying = intercept.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        #
        # The propertyInstance variable is a reference to the holder, so it doesn't
        # change in any case, hence assertIs.
        self.assertIs(propertyInstance, intercept.destinationTupleItems)
        self.assertEqual((1,3), intercept.destinationTuple)
        self.assertEqual(
            intercept.destinationTuple, intercept.destinationTupleItems[:])
        
        intercept.destinationTupleItems[2:2] = (4,)
        self.assertIsNot(underlaying, intercept.destinationTuple)
        underlaying = intercept.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(propertyInstance, intercept.destinationTupleItems)
        self.assertEqual((1,3,4), intercept.destinationTuple)
        self.assertEqual(
            intercept.destinationTuple, intercept.destinationTupleItems[:])
        
        intercept.destinationTupleItems[0:1] = (5, 6, 7)
        self.assertIsNot(underlaying, intercept.destinationTuple)
        underlaying = intercept.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(propertyInstance, intercept.destinationTupleItems)
        self.assertEqual((5,6,7,3,4), intercept.destinationTuple)
        self.assertEqual(
            intercept.destinationTuple, intercept.destinationTupleItems[:])
        
        del intercept.destinationTupleItems[1]
        self.assertIsNot(underlaying, intercept.destinationTuple)
        underlaying = intercept.destinationTuple
        self.assertIsInstance(underlaying, tuple)
        self.assertIs(propertyInstance, intercept.destinationTupleItems)
        self.assertEqual((5,7,3,4), intercept.destinationTuple)
        self.assertEqual(
            intercept.destinationTuple, intercept.destinationTupleItems[:])
    
    def test_readonly_alternative_setitem(self):
        intercept = InterceptAlternative(
            tuple(), tuple(), ReadOnly([1,2]), "three")
        propertyInstance = intercept.destinationReadOnlyItems
        underlaying = intercept.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertEqual([1,2], intercept.destinationReadOnly[:])

        intercept.destinationReadOnlyItems[1] = 3
        #
        # In all cases, the underlying property must change, because it is a
        # tuple and therefore immutable, hence assertIsNot.
        self.assertIsNot(underlaying, intercept.destinationReadOnly)
        underlaying = intercept.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        #
        # The propertyInstance variable is a reference to the holder, so it doesn't
        # change in any case, hence assertIs.
        self.assertIs(propertyInstance, intercept.destinationReadOnlyItems)
        self.assertEqual([1,3], intercept.destinationReadOnly)
        self.assertEqual(
            intercept.destinationReadOnly, intercept.destinationReadOnlyItems[:])
        
        intercept.destinationReadOnlyItems[2:2] = (4,)
        self.assertIsNot(underlaying, intercept.destinationReadOnly)
        underlaying = intercept.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(propertyInstance, intercept.destinationReadOnlyItems)
        self.assertEqual([1,3,4], intercept.destinationReadOnly)
        self.assertEqual(
            intercept.destinationReadOnly, intercept.destinationReadOnlyItems[:])
        
        intercept.destinationReadOnlyItems[0:1] = (5, 6, 7)
        self.assertIsNot(underlaying, intercept.destinationReadOnly)
        underlaying = intercept.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(propertyInstance, intercept.destinationReadOnlyItems)
        self.assertEqual([5,6,7,3,4], intercept.destinationReadOnly)
        self.assertEqual(
            intercept.destinationReadOnly, intercept.destinationReadOnlyItems[:])
        
        del intercept.destinationReadOnlyItems[1]
        self.assertIsNot(underlaying, intercept.destinationReadOnly)
        underlaying = intercept.destinationReadOnly
        self.assertIsInstance(underlaying, ReadOnly)
        self.assertIs(propertyInstance, intercept.destinationReadOnlyItems)
        self.assertEqual([5,7,3,4], intercept.destinationReadOnly)
        self.assertEqual(
            intercept.destinationReadOnly, intercept.destinationReadOnlyItems[:])
    
    def test_list_alternative_setitem(self):
        list_ = [1,2]
        intercept = InterceptAlternative(tuple(), list_, tuple(), "three")
        propertyInstance = intercept.destinationListItems
        underlaying = intercept.destinationList
        self.assertEqual(list_, propertyInstance[:])
        self.assertIs(list_, underlaying)
    
        intercept.destinationListItems[1] = 3
        #
        # The underlying property shouldn't change, because it is mutable.
        self.assertIs(underlaying, intercept.destinationList)
        self.assertIs(propertyInstance, intercept.destinationListItems)
        self.assertIs(list_, underlaying)
        self.assertEqual([1,3], list_)
        self.assertEqual(list_, intercept.destinationListItems[:])
        
        intercept.destinationListItems[2:2] = [4]
        self.assertIs(underlaying, intercept.destinationList)
        self.assertIs(propertyInstance, intercept.destinationListItems)
        self.assertIs(list_, underlaying)
        self.assertEqual([1,3,4], list_)
        self.assertEqual(list_, intercept.destinationListItems[:])
        
        intercept.destinationListItems[0:1] = (5, 6, 7)
        self.assertIs(underlaying, intercept.destinationList)
        self.assertIs(propertyInstance, intercept.destinationListItems)
        self.assertIs(list_, underlaying)
        self.assertEqual([5,6,7,3,4], list_)
        self.assertEqual(list_, intercept.destinationListItems[:])
        
        del intercept.destinationListItems[1]
        self.assertIs(underlaying, intercept.destinationList)
        self.assertIs(propertyInstance, intercept.destinationListItems)
        self.assertIs(list_, underlaying)
        self.assertEqual([5,7,3,4], list_)
        self.assertEqual(list_, intercept.destinationListItems[:])
    
    def test_list_alternative_getitem(self):
        listItem1 = [None]
        list_ = [1, listItem1]
        intercept = InterceptAlternative(tuple(), list_, tuple(), "three")
        self.assertEqual(1, intercept.destinationListItems[0])
        self.assertIs(listItem1, intercept.destinationListItems[1])
        self.assertNotIsInstance(intercept.destinationListItems, list)
    
    def test_alternative_method(self):
        intercept = InterceptAlternative([1,2], tuple(), tuple(), "three")
        self.assertEqual(2, len(intercept.destinationTupleItems))
        self.assertEqual(1, intercept.destinationTupleItems.count(2))

# ToDo:
# Test that the attribute changes, for example from list to tuple, if cast=NONE
# Test ISDIFFERENTNOW vs ISDIFFERENTTHEN
# Test two subclass instances.
# -   Test setting the intercept property as a whole: bypass_setter.
# -   Test like bypass_setitem.
