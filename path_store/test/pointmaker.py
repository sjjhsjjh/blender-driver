#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
from .principal import PointMakerTracker, Principal
#
# Modules under test.
import pathstore

class PointMaker(PointMakerTracker):
    def principal_point_maker(self, path, index, point):
        return_ = None
        if index == self.principalIndex:
            if isinstance(point, Principal):
                return_ = point
            else:
                return_ = Principal()
        return self.point_maker(path, index, point, return_)
        
    def __init__(self, principalIndex=0):
        super().__init__()
        self.principalIndex = principalIndex

class TestPointMaker(unittest.TestCase):
    def test_empty(self):
        pointMaker = PointMaker()
        point = pathstore.merge(
            None, None, point_maker=pointMaker.principal_point_maker)
        self.assertEqual(len(pointMaker.makerTrack), 0)
        self.assertIs(point, None)
        
        point0 = "discarded"
        value = "replaced"
        point1 = pathstore.merge(
            point0, value, point_maker=pointMaker.principal_point_maker)
        self.assertEqual(len(pointMaker.makerTrack), 0)
        self.assertIsNot(point1, point0)
        self.assertIs(point1, value)

    def test_principal_root(self):
        pointMaker = PointMaker()
        point0 = None
        path = ('testAttr', 'de', 'fgh', 'ij', 'kl')
        expected = [
            (str(path), index, str(point0)) for index in range(len(path))]
        point1 = pathstore.merge(
            point0, None, path, point_maker=pointMaker.principal_point_maker)
        self.assertEqual(pointMaker.makerTrack, expected)
        self.assertIsInstance(point1, Principal)
        self.assertEqual(point1.testAttr, {'de':{'fgh':{'ij':{'kl': None}}}})
        
        pointMaker = PointMaker()
        point0 = Principal()
        point1 = pathstore.merge(
            point0, None, path, point_maker=pointMaker.principal_point_maker)
        expected[0] = pointMaker.tracker_for(path, 0, point0)
        self.assertEqual(pointMaker.makerTrack, expected)
        self.assertIs(point1, point0)
        
        pointMaker = PointMaker()
        point0 = None
        path = ('de', 'fgh', 'ij', 'kl')
        with self.assertRaises(AssertionError) as context:
            point1 = pathstore.merge(
                point0, None, path
                , point_maker=pointMaker.principal_point_maker)
        index = 0
        assertionError = AssertionError("".join((
            "type was None twice at ", str(pointMaker.lastPoint)
            ," path:", str(path), " index:", str(index)
            , " leg:", pathstore.str_quote(path[index]), ".")))
        self.assertEqual(str(context.exception), str(assertionError))

    def test_principal_leaf(self):
        pointMaker = PointMaker(3)
        point0 = None
        path = ('de', 'fgh', 'ij', 'testAttr')
        value = "valueTest"
        expected = [
            (str(path), index, str(point0)) for index in range(len(path))]
        point1 = pathstore.merge(
            point0, value, path, point_maker=pointMaker.principal_point_maker)
        self.assertEqual(pointMaker.makerTrack, expected)
        self.assertEqual(point1, {'de':{'fgh':{'ij':pointMaker.lastPoint}}})
        self.assertEqual(pointMaker.lastPoint.testAttr, value)

    def test_principal_middle(self):
        pointMaker = PointMaker(3)
        point0 = None
        path0 = ('de', 2, 'ij')
        path1 = ('testAttr', 1, 0)
        path = path0 + path1
        value = "arrayValue"
        expected = [
            (str(path), index, str(point0)) for index in range(len(path))]
        point1 = pathstore.merge(
            point0, value, path, point_maker=pointMaker.principal_point_maker)
        self.assertEqual(pointMaker.makerTrack, expected)
        principal = pathstore.get(point1, path0)
        self.assertEqual(point1, {'de':[None, None, {'ij':principal}]})
        self.assertIsInstance(principal, Principal)
        self.assertEqual(principal.testAttr, [None, [value]])

    def test_principal_not_reached(self):
        pointMaker = PointMaker(4)
        point0 = None
        path = ('de', 'fgh', 'ij', 'kl')
        expected = [
            (str(path), index, str(point0)) for index in range(len(path))]
        point1 = pathstore.merge(
            point0, None, path, point_maker=pointMaker.principal_point_maker)
        self.assertEqual(pointMaker.makerTrack, expected)
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
            call(('outvaluearr', 0, 'invalue'), 0, None),
            call(('outvaluearr', 0, 'invalue'), 1, None),
            call(('outvaluearr', 0, 'invalue'), 2, None),
            #
            # The last parameter on the next line is the `expected` structure,
            # above. The parameter as passed would have been just the
            # `outvaluearr` hierarchy, but by the time the value is checked, it
            # has been modified, because pathstore.merge operates in place on
            # the data structure. 
            call(('outvaluedict', 'invalue'), 0, expected),
            call(('outvaluedict', 'invalue'), 1, None)
        ]


        mock = Mock(side_effect=pathstore.default_point_maker)
        point = make_structure(mock)
        self.assertEqual(point, expected)
        mock.assert_has_calls(expectedCalls)
        
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
        mock.assert_has_calls(expectedCalls)
