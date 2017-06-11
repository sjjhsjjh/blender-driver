#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test utility classes.
Classes in this module can be tested like:

    python3 path_store/test.py TestPrincipal
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
from hosted import HostedProperty

class SetCounter(object):
    """Class that provides a counter in its instance."""
    @property
    def setterCount(self):
        return self._setterCount
    
    def incrementSetCount(self, amount=1):
        self._setterCount += amount

    def __init__(self, countStart=0):
        self._setterCount = countStart

class TupleHost(object):
    hostedTuple = None
    
    def __init__(self, tupleValue):
        try:
            self.hostedTuple = tuple(tupleValue)
        except TypeError:
            self.hostedTuple = tuple()

class Principal(SetCounter):
    
    hostedTuple = HostedProperty('hostedTuple', 'tupleHost')
    
    @property
    def tupleHost(self):
        return self._tupleHost
    
    @property
    def countedStr(self):
        """String property that counts whenever it is set."""
        return self._countedStr
    @countedStr.setter
    def countedStr(self, countedStr):
        self._countedStr = countedStr
        self.incrementSetCount()
    
    def __init__(self, value=None, hostedTuple=None):
        self.testAttr = value
        self._countedStr = None
        self.hostedTuple = None
        self._tupleHost = TupleHost(hostedTuple)
        super().__init__()

class SetCounterDict(dict, SetCounter):
    """Dictionary subclass that counts whenever an item is set."""
    def __setitem__(self, key, value):
        self.incrementSetCount()
        return dict.__setitem__(self, key, value)

    def __init__(self, *args, **kwargs):
        SetCounter.__init__(self)
        dict.__init__(self, *args, **kwargs)

class SetCounterList(list, SetCounter):
    """List subclass that counts whenever an item is set."""
    def __setitem__(self, key, value):
        self.incrementSetCount()
        # The previous line ignores possible complexities:
        # -   key could be a slice.
        # -   value could be an iterable.
        # Why? Because the purpose of this class is only to test whether the
        # setter was called at all.
        #
        return list.__setitem__(self, key, value)

    def __init__(self, *args, **kwargs):
        SetCounter.__init__(self)
        list.__init__(self, *args, **kwargs)

class PointMakerTracker(object):
    """Class that provides a Path Store point maker implementation that tracks
    every call.
    """
    def tracker_for(self, path, index, point):
        return str(path), index, str(point)

    def track(self, path, index, point):
        self.makerTrack.append(self.tracker_for(path, index, point))
        return self.makerTrack
    
    def point_maker(self, path, index, point, return_=None):
        self.track(path, index, point)
        if return_ is None:
            return_ = pathstore.default_point_maker(path, index, point)
        self.lastPoint = return_
        return return_

    def __init__(self):
        self.makerTrack = []
        self.lastPoint = None

class TestPrincipal(unittest.TestCase):
    """Unit tests for the Principal utility module."""
    def test_set_count(self):
        principal = Principal()
        self.assertEqual(principal.setterCount, 0)
        principal.countedStr = "one"
        self.assertEqual(principal.setterCount, 1)

    def test_set_count_dict(self):
        setCounterDict = SetCounterDict({'blab': 2})
        self.assertEqual(setCounterDict.setterCount, 0)
        setCounterDict['blib'] = "one"
        self.assertEqual(setCounterDict.setterCount, 1)

    def test_set_count_list(self):
        setCounterList = SetCounterList(("first", "second"))
        self.assertEqual(setCounterList.setterCount, 0)
        setCounterList[1] = "one"
        self.assertEqual(setCounterList.setterCount, 1)
        setCounterList[:] = ["aye", "bee", "see"]
        self.assertEqual(setCounterList.setterCount, 2)
    
    def test_point_maker_tracker(self):
        pointMakerTracker = PointMakerTracker()
        self.assertEqual(pointMakerTracker.makerTrack, [])
        path = ("abc", "de", "fgh", "ij", "kl")
        point0 = 4
        expected = [(str(path), 3, str(point0))]
        point1 = pointMakerTracker.track(path, 3, point0)
        self.assertEqual(pointMakerTracker.makerTrack, expected)

        point1 = pointMakerTracker.track(path, 3, point0)
        self.assertEqual(pointMakerTracker.makerTrack, expected * 2)

    def test_point_maker_tracker_insert(self):
        pointMakerTracker = PointMakerTracker()
        point0 = None
        path = 0
        expected = [pointMakerTracker.tracker_for((path,), 0, point0)]
        point1 = pathstore.merge(
            point0, None, path, point_maker=pointMakerTracker.point_maker)
        self.assertEqual(pointMakerTracker.makerTrack, expected)
        
        pointMakerTracker = PointMakerTracker()
        point0 = None
        path = ('abc', 'de', 'fgh', 'ij', 'kl')
        expected = [
            (str(path), index, str(point0)) for index in range(len(path))]
        point1 = pathstore.merge(
            point0, None, path, point_maker=pointMakerTracker.point_maker)
        self.assertEqual(pointMakerTracker.makerTrack, expected)
        self.assertEqual(point1, {'abc':{'de':{'fgh':{'ij':{'kl': None}}}}})

    def test_tuple_holder(self):
        tupleHost = TupleHost([None])
        tuple_ = (None,)
        self.assertEqual(tupleHost.hostedTuple, tuple_)
        self.assertIsInstance(tupleHost.hostedTuple, tuple)
        
        principal = Principal(None, [1,2])
        self.assertEqual([1,2], list(principal.hostedTuple[:]))

        principal.hostedTuple[1] = 3
        self.assertEqual([1,3], list(principal.hostedTuple[:]))
        
        principal.hostedTuple[2:2] = (4,)
        self.assertEqual([1,3,4], list(principal.hostedTuple[:]))
        
        principal.hostedTuple[0:1] = (5, 6, 7)
        self.assertEqual([5,6,7,3,4], list(principal.hostedTuple[:]))
        
        del principal.hostedTuple[1]
        self.assertEqual([5,7,3,4], list(principal.hostedTuple[:]))
