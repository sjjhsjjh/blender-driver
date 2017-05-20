#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test utility classes.
Classes in this module can be tested like:

    python3 path-store/test.py TestPrincipal
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

class SetCounter(object):
    @property
    def setterCount(self):
        return self._setterCount
    
    def incrementSetCount(self, amount=1):
        self._setterCount += amount

    def __init__(self, countStart=0):
        self._setterCount = countStart

class Principal(SetCounter):
    @property
    def countedStr(self):
        return self._countedStr
    @countedStr.setter
    def countedStr(self, countedStr):
        self._countedStr = countedStr
        self.incrementSetCount()
    
    def __init__(self, value=None):
        self.testAttr = value
        self._countedStr = None
        super().__init__()

class SetCounterDict(dict, SetCounter):
    def __setitem__(self, key, value):
        self.incrementSetCount()
        print('SetCounterDict', key, value)
        return dict.__setitem__(self, key, value)

    def __init__(self, *args, **kwargs):
        SetCounter.__init__(self)
        dict.__init__(self, *args, **kwargs)

class SetCounterList(list, SetCounter):
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

class TestPrincipal(unittest.TestCase):
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
