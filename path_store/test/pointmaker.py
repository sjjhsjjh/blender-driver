#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit test module. Tests in this module can be run like:

    python3 path_store/test.py TestPointMaker
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
# Utilities.
# from .principal import PointMakerTracker, Principal
#
# Modules under test.
import pathstore

class Principal:
    testAttr = None

class PointMaker:
    '''\
    Class for unit testing of point maker mechanism. The principal_point_maker
    copies its input parameters, which is necessary in case one of them is a
    list that is subsequently modified. The Mock class doesn't copy the
    parameters, only references to them.
    '''
    def principal_point_maker(self, path, index, point):
        if index >= len(path):
            raise ValueError(
                "Point maker index too big index:{} path:{} length:{}.".format(
                    index, path, len(path)))
        return_ = None
        if index == self._principalIndex:
            return_ = point if isinstance(point, Principal) else Principal()
        else:
            return_ = pathstore.default_point_maker(path, index, point)
        self._lastPoint = return_
        self._calls.append(call(path[:], index, point))
        return return_
    
    def reset(self):
        del self._lastPoint
        self._calls = []
    
    @property
    def lastPoint(self):
        return self._lastPoint
    
    @property
    def calls(self):
        return self._calls
        
    def __init__(self, principalIndex):
        self._principalIndex = principalIndex
        self._calls = []

class TestPointMaker(unittest.TestCase):
    def test_empty(self):
        mock = Mock(side_effect=pathstore.default_point_maker)

        point = pathstore.merge(None, None, point_maker=mock)
        self.assertEqual(mock.call_count, 0)
        self.assertIs(point, None)
        
        point0 = "discarded"
        value = "replaced"
        point1 = pathstore.merge(point0, value, point_maker=mock)
        self.assertEqual(mock.call_count, 0)
        self.assertIsNot(point1, point0)
        self.assertIs(point1, value)
    
    def test_principal(self):
        principal = Principal()
        self.assertTrue(hasattr(principal, 'testAttr'))
        pointMaker = PointMaker(0)
        with self.assertRaises(ValueError):
            pointMaker.principal_point_maker(('one', 'two'), 2, None)
        with self.assertRaises(ValueError):
            pointMaker.principal_point_maker(('one', 'two'), 20, None)

    def test_principal_root(self):
        pointMaker = PointMaker(0)
        path = ['testAttr', 'de', 'fgh', 'ij', 'kl']
        #
        # Start with None.
        point0 = None
        mock = Mock(side_effect=pointMaker.principal_point_maker)
        point1 = pathstore.merge(point0, None, path, point_maker=mock)
        self.assertEqual(mock.call_count, len(path))
        for index in range(len(path)):
            self.assertEqual(
                mock.call_args_list[index], call(path, index, None))
            #
            # Following code extracts positional arguments and makes an
            # assertion about each. It is equivalent to the single assertion
            # above and is kept only for reference.
            callPositional = mock.call_args_list[index][0]
            self.assertEqual(callPositional[0], path)
            self.assertEqual(callPositional[1], index)
            self.assertEqual(callPositional[2], None)
        self.assertIsInstance(point1, Principal)
        self.assertEqual(point1.testAttr, {'de':{'fgh':{'ij':{'kl': None}}}})
        #
        # Start with an object of the required type. It should be passed to the
        # first point maker call, and shouldn't be replaced.
        principal = Principal()
        point0 = principal
        mock.reset_mock()
        point1 = pathstore.merge(point0, None, path, point_maker=mock)
        self.assertEqual(
            mock.call_args_list, [
                call(path, index, principal if index == 0 else None
                     ) for index in range(len(path))])
        self.assertIs(point1, point0)
        self.assertIs(point1, principal)
        #
        # Try a path that can't be rooted in the required type.
        point0 = None
        path = ['de', 'fgh', 'ij', 'kl']
        with self.assertRaises(AssertionError) as context:
            point1 = pathstore.merge(point0, None, path, point_maker=mock)
        index = 0
        assertionError = AssertionError("".join((
            "pointType was None twice at ", str(pointMaker.lastPoint)
            ," path:", str(path), " index:", str(index)
            , " leg:", pathstore.str_quote(path[index]), ".")))
        self.assertEqual(str(context.exception), str(assertionError))

    def test_principal_leaf(self):
        pointMaker = PointMaker(3)
        mock = Mock(side_effect=pointMaker.principal_point_maker)
        point0 = None
        path = ['de', 'fgh', 'ij', 'testAttr']
        value = "valueTest"
        point1 = pathstore.merge(point0, value, path, point_maker=mock)
        self.assertEqual(mock.call_args_list, [
            call(path, index, None) for index in range(len(path))])
        self.assertEqual(point1, {'de':{'fgh':{'ij':pointMaker.lastPoint}}})
        self.assertEqual(pointMaker.lastPoint.testAttr, value)
        self.assertIsInstance(pointMaker.lastPoint, Principal)

        mock.reset_mock()
        point0 = None
        path0 = ['de', 2, 'ij']
        path1 = ['testAttr', 1, 0]
        path = path0 + path1
        value = "arrayValue"
        point1 = pathstore.merge(point0, value, path, point_maker=mock)
        self.assertEqual(mock.call_args_list, [
            call(path, index, None) for index in range(len(path))])
        principal = pathstore.get(point1, path0)
        self.assertEqual(point1, {'de':[None, None, {'ij':principal}]})
        self.assertIsInstance(principal, Principal)
        self.assertEqual(principal.testAttr, [None, [value]])
        #
        # Replacing with a dictionary should result in an object if the point
        # maker specifies that.
        mock.reset_mock()
        pointMaker.reset()
        point0 = None
        path = ['de', 2, 'ij']
        value0 = "Value in dictionary."
        value = {'testAttr': value0}
        point1 = pathstore.replace(point0, value, path, point_maker=mock)
        principal = pathstore.get(point1, path)
        self.assertEqual(point1, {'de':[None, None, {'ij':principal}]})
        self.assertIsInstance(principal, Principal)
        self.assertIs(principal.testAttr, value0)
        self.assertEqual(pointMaker.calls, [
            call(path, index, None) for index in range(len(path))
            ] + [
            call(path + [None], len(path), None),
            call(list(path) + ['testAttr'], len(path), principal)])
        #
        # Replacing with an empty dictionary should result in an object if the
        # point maker specifies that.
        mock.reset_mock()
        pointMaker.reset()
        point0 = None
        path = ['de', 2, 'ij']
        point1 = pathstore.replace(point0, {}, path, point_maker=mock)
        principal = pathstore.get(point1, path)
        self.assertEqual(point1, {'de':[None, None, {'ij':principal}]})
        self.assertIsInstance(principal, Principal)
        self.assertEqual(pointMaker.calls, [
            call(path, index, None) for index in range(len(path))
            ] + [
            call(path + [None], len(path), None)])
        #
        # Replacing with a None should result in None, regardless of what the
        # point maker specifies. The last invocation of the point maker in the
        # previous test shouldn't take place here because the point maker
        # doesn't get invoked after the end of the path has been reached.
        mock.reset_mock()
        pointMaker.reset()
        point0 = None
        path = ['de', 2, 'ij']
        point1 = pathstore.replace(point0, None, path, point_maker=mock)
        self.assertEqual(point1, {'de':[None, None, {'ij':None}]})
        principal = pathstore.get(point1, path)
        self.assertEqual(pointMaker.calls, [
            call(path, index, None) for index in range(len(path))])

    def test_principal_not_reached(self):
        pointMaker = PointMaker(4)
        mock = Mock(side_effect=pointMaker.principal_point_maker)
        point0 = None
        path = ['de', 'fgh', 'ij', 'kl']
        point1 = pathstore.merge(point0, None, path, point_maker=mock)
        self.assertEqual(mock.call_args_list, [
            call(path, index, None) for index in range(len(path))])
        self.assertEqual(point1, {'de':{'fgh':{'ij':{'kl': None}}}})

    def test_principal_in_array(self):
        arrinvalue = "scalar"
        expected = {
            'outvaluearr': [
                { # *Test point
                    'invalue': arrinvalue
                }
            ],
            'outvaluedict': {
                'invalue': "otherscalar"
            }
        }
        #
        # *Test point will be a dictionary without the point maker, but an
        # object with the point maker.
        #
        
        def make_structure(point_maker):
            """Execute sequence of Path Store calls to build the structure."""
            root = None
            root = pathstore.merge(
                root, arrinvalue, ('outvaluearr', 0, 'invalue'), point_maker)
            root = pathstore.merge(
                root, "otherscalar", ('outvaluedict', 'invalue'), point_maker)
            return root

        expectedCalls = [
            call(['outvaluearr', 0, 'invalue'], index, None
                ) for index in range(3)] + [
            #
            # The last parameter on the next line is the `expected` structure,
            # above. The parameter as passed would have been just the
            # `outvaluearr` hierarchy, but by the time the value is checked, it
            # has been modified, because pathstore.merge operates in place on
            # the data structure. 
            call(['outvaluedict', 'invalue'], 0, expected),
            call(['outvaluedict', 'invalue'], 1, None)]


        mock = Mock(side_effect=pathstore.default_point_maker)
        point = make_structure(mock)
        self.assertEqual(point, expected)
        self.assertEqual(mock.call_args_list, expectedCalls)
        
        class PointPrincipal(Mock):
            invalue = None
            
            def __repr__(self):
                return str({'PointPrincipal':{'invalue': self.invalue}})
            
            def __eq__(self, other):
                return (
                    isinstance(other, PointPrincipal)
                    and other.invalue == self.invalue)

        pointStrings = []
        def object_point_maker(path, index, point):
            #
            # Intention of the next line is to take an snapshot of the last
            # parameter as it was at call time. The snapshot isn't formally
            # useful for comparison, because the order of dictionary keys isn't
            # guarranteed to be the same. 
            pointStrings.append(str(point))
            #
            # Next line has index == 2, which is one more than the level at
            # which the object is to be created. The index == 1 level can get a
            # None in order to build the array.
            if path[0] == 'outvaluearr' and index == 2:
                return PointPrincipal()
            else:
                return pathstore.default_point_maker(path, index, point)

        # Adjust the `expected` hierarchy to have an object in the expected
        # location, instead of a dictionary.
        expectedObject = PointPrincipal()
        expectedObject.invalue = arrinvalue
        expected['outvaluearr'][0] = expectedObject
        #
        # Execute the test.
        mock = Mock(side_effect=object_point_maker)
        point = make_structure(mock)
        self.assertEqual(point, expected)
        self.assertEqual(mock.call_args_list, expectedCalls)

    def test_empty_path(self):
        pointMaker = PointMaker(0)
        mock = Mock(side_effect=pointMaker.principal_point_maker)
        #
        # Merge should always merge into a new object. A test for that with the
        # default point maker is in That test is in TestMerge.test_into_none.
        #
        # Test with a custom point maker is here. We expect the point maker to
        # be called twice: once for the root, once for the dictionary element.
        attrValue = {'a': "dictionary"}
        value = {'testAttr':attrValue}
        point0 = None
        point1 = pathstore.merge(point0, value, point_maker=mock)
        self.assertEqual(mock.call_args_list, [
            call(['testAttr'], 0, None), call(['testAttr', 'a'], 1, None)])
        self.assertIsInstance(point1, Principal)
        #
        # Note that the merge-ness cascades, so the attrValue dictionary is
        # copied into the testAttr property, not assigned to it.
        self.assertIsNot(point1.testAttr, attrValue)
        self.assertEqual(point1.testAttr, attrValue)
        #
        # Replace should put the value, if it is the required type. A test for
        # that with the default point maker is in TestReplace.test_into_none.
        #
        # Test for that with a custom point maker is here. There isn't a path,
        # so the point maker is called with a made-up path: (None,).
        value = Principal()
        point0 = None
        mock.reset_mock()
        point1 = pathstore.replace(point0, value, point_maker=mock)
        self.assertIs(point1, value)
        self.assertEqual(mock.call_args_list, [call([None], 0, None)])
