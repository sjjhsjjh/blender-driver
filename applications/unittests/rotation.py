#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver unit test that can be run from the unittest application.

This module is intended for use within Blender Driver and can only be used from
within Blender."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for mathematical operations needed to decompose a rotation matrix.
# https://docs.python.org/3/library/math.html
from math import degrees, radians
#
# Unit test module.
# https://docs.python.org/3/library/unittest.html
# No need to import here because it is already imported by the Custom TestCase,
# see below.
# import unittest
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Euler, Vector
#
# Local imports.
#
# Custom TestCase
from applications.unittest import TestCaseWithApplication
#
# Modules under test: 
from path_store.blender_game_engine import camera
from path_store.blender_game_engine.rotation import Rotation
from path_store import pathstore

from diagnostic.analysis import fall_analysis

class OrientationHost:
    def _get_orientation(self):
        return self._orientation
    def _set_orientation(self, orientation):
        self._orientation = orientation
    
    @property
    def orientation(self):
        return self._orientation
    
    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, values):
        if values is None:
            del self._rotation[:]
        else:
            self._rotation[:] = tuple(values)
    @rotation.deleter
    def rotation(self):
        del self._rotation[:]
    
    def __init__(self):
        self._orientation = Euler((0,0,0)).to_matrix()
        self._rotation = Rotation(self._get_orientation, self._set_orientation)

def _degreesEuler(values, order=None):
    valuesRadian = tuple(radians(value) for value in values)
    if order is None:
        return Euler(valuesRadian)
    else:
        return Euler(valuesRadian, order)

class TestRotation(TestCaseWithApplication):
    def test_angular_move(self):
        def angular_move(current, target, speed=None):
            speedSign, targetRadians, changeRadians = (
                camera.angular_move(radians(current), radians(target))
                if speed is None else
                camera.angular_move(radians(current), radians(target), speed))
            return speedSign, degrees(targetRadians), degrees(changeRadians)
        
        speed, target, change = angular_move(0.0, 10.0)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, 10.0)
        self.assertAlmostEqual(change, 10.0)

        speed, target, change = angular_move(0.0, -10.0)
        self.assertEqual(speed, -1)
        self.assertAlmostEqual(target, -10.0)
        self.assertAlmostEqual(change, 10.0)
        
        speed, target, change = angular_move(350, -5.0)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, 355.0)
        self.assertAlmostEqual(change, 5.0)
        
        speed, target, change = angular_move(-10, -5.0)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, -5.0)
        self.assertAlmostEqual(change, 5)
        
        speed, target, change = angular_move(0, 185)
        self.assertEqual(speed, -1)
        self.assertAlmostEqual(target, -175)
        self.assertAlmostEqual(change, 175)

        speed, target, change = angular_move(5, 190, 10)
        self.assertEqual(speed, -10)
        self.assertAlmostEqual(target, -170)
        self.assertAlmostEqual(change, 175)

        speed, target, change = angular_move(165, -230, 1)
        self.assertEqual(speed, -1)
        self.assertAlmostEqual(target, 130)
        self.assertAlmostEqual(change, 35)

        speed, target, change = angular_move(-178, -7)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, -7)
        self.assertAlmostEqual(change, 171)

        speed, target, change = angular_move(180, -2)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, 358)
        self.assertAlmostEqual(change, 178)

        speed, target, change = angular_move(-180, -2)
        self.assertEqual(speed, 1)
        self.assertAlmostEqual(target, -2)
        self.assertAlmostEqual(change, 178)

    def test_euler(self):
        # Creating an Euler with a specified order doesn't change the semantics
        # of the values parameter.
        self.assertSequenceEqual(_degreesEuler((0, 0, 90), 'XYZ')[:],
                                 _degreesEuler((0, 0, 90), 'ZXY')[:])
        
        # Changing the order doesn't adjust the values.
        euler0 = _degreesEuler((0, 90, 90), 'XYZ')
        euler1 = euler0.copy()
        euler1.order = 'ZXY'
        self.assertSequenceEqual(euler0[:], euler1[:])

        # Adding a rotation in a different dimension is the same as specifying
        # it in the constructor, if the dimension of the added rotation is after
        # the initial rotation in the Euler order ...
        euler0 = _degreesEuler((90, 0, 90), 'XYZ')
        euler1 = _degreesEuler((90, 0, 0), 'XYZ')
        euler1.rotate(_degreesEuler((0, 0, 90), 'XYZ'))
        self.assertSequenceEqual(euler0[:], euler1[:])
        #
        # ... but not if the added rotation is before the initial rotation.
        euler0 = _degreesEuler((90, 0, 90), 'XYZ')
        euler1 = _degreesEuler((0, 0, 90), 'XYZ')
        euler1.rotate(_degreesEuler((90, 0, 0), 'XYZ'))
        same = True
        # Hmm. Python unittest doesn't seem to have a single assertion for
        # sequence not equal.
        for index, value in enumerate(euler0):
            if value != euler1[index]:
                same = False
                break
        self.assertFalse(same)

        # Don't know what make_compatible does really. The reference
        # documentation states that it ignores order.
        # 
        # eulers.append(eulers[-1].copy())
        # eulers[-1].make_compatible(eulers[2])


        # Handy Euler dumping code.
        # for index, euler in enumerate(eulers):
        #     print(index, euler, tuple(
        #         '{:.1f}'.format(degrees(item)) for item in euler[:]))
 
    def test_rotation_class(self):
        # Create a Rotation object and check that it changes in the same way as
        # a plain Euler. This is the simple case without incremental
        # assignments.
        # There are three rotations, in X, then in Z, last in Y. Each is
        # completed in two steps of 45 degrees. The Euler order is changed
        # before the first step of each so that the dimension being changed is
        # last. 
        host = OrientationHost()
        
        # Test that setting silly values still recovers the value.
        host.rotation.x = radians(720)
        self.assertEqual(host.rotation.x, radians(720))
        host.rotation.y = radians(-1720)
        self.assertEqual(host.rotation.y, radians(-1720))
        #
        # But after deleting, sensible values are returned instead.
        host.rotation = (radians(360 + 45), 0, 0)
        del host.rotation
        self.assertAlmostEqual(host.rotation.x, radians(45))
        
        # Reset the rotation.
        host.rotation = (0, 0, 0)
        euler = _degreesEuler((0, 0, 0), 'YZX')
        host.rotation.order = 'YZX'
        euler.x = radians(45)
        host.rotation.x = radians(45)
        # Delete the rotation to stymie rotation.setCache, which will return the
        # value set, not the decomposed value from the Euler.
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)
        euler.x = radians(90)
        host.rotation.x = radians(90)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)

        matrix = euler.to_matrix()
        euler = matrix.to_euler('XYZ')
        host.rotation.order = 'XYZ'
        euler.z = radians(45)
        host.rotation.z = radians(45)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)
        euler.z = radians(90)
        host.rotation.z = radians(90)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)

        matrix = euler.to_matrix()
        euler = matrix.to_euler('ZXY')
        host.rotation.order = 'ZXY'
        euler.y = radians(45)
        host.rotation.y = radians(45)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)
        euler.y = radians(90)
        host.rotation.y = radians(90)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)

        # Create a Rotation object and check that it changes in the same way as
        # a plain Euler. This is the tricky case, with increments, but is
        # otherwise the same as the previous case, see notes there.
        host = OrientationHost()

        euler = _degreesEuler((0, 0, 0), 'YZX')
        host.rotation.order = 'YZX'
        euler.x += radians(45)
        host.rotation.x += radians(45)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)
        euler.x += radians(45)
        host.rotation.x += radians(45)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)

        matrix = euler.to_matrix()
        euler = matrix.to_euler('XYZ')
        host.rotation.order = 'XYZ'
        euler.z -= radians(45)
        host.rotation.z -= radians(45)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)
        euler.z -= radians(45)
        host.rotation.z -= radians(45)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)

        matrix = euler.to_matrix()
        euler = matrix.to_euler('ZXY')
        host.rotation.order = 'ZXY'
        euler.y += radians(45)
        host.rotation.y += radians(45)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)
        euler.y += radians(45)
        host.rotation.y += radians(45)
        del host.rotation
        self.assertSequenceEqual(euler[:], host.rotation[:])
        self.assertEqual(euler, host.rotation.euler)

    def test_rotation_rest(self):
        host = OrientationHost()
        host.rotation.order = 'ZXY'
        host.rotation.y += radians(45)

        # Next line results in Rotation.__delitem__ being called, which discards
        # the Euler.
        del host.rotation
        #
        # Access to the rotation.euler property in the next line causes the
        # Euler to be generated again by decomposition of the host orientation. 
        self.assertEqual(host.orientation.to_euler('ZXY'), host.rotation.euler)

        # Save the decomposed rotation, then discard the Euler again.
        rotation = host.rotation.euler[:]
        del host.rotation
        #
        # Test that the same value comes back from Path Store get.
        self.assertSequenceEqual(pathstore.get(host, ('rotation',)), rotation)

        # Test that Path Store descent works after deletion.
        del host.rotation
        self.assertEqual(
            (pathstore.PointType.LIST, rotation[2], None)
            , pathstore.descend(host.rotation, 2))

    def test_vector_rotation(self):
        zAxis0 = Vector((0, 0, 1))

        zAxis1 = zAxis0.copy()
        zAxis1.rotate(_degreesEuler((90, 0, 0)))

        host = OrientationHost()
        host.rotation = (radians(90), 0, 0)
        zAxis2 = zAxis0.copy()
        zAxis2.rotate(host.orientation)
        self.assertSequenceEqual(zAxis1[:], zAxis2[:])

        # Reset the host to an identity orientation.
        host.rotation = (0, 0, 0)
        zAxis3 = zAxis0.copy()
        zAxis3.rotate(host.orientation)
        self.assertSequenceEqual(zAxis0[:], zAxis3[:])
        
