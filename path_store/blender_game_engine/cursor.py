#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for use with Blender Game Engine.

Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module that facilitates container subclasses.
# https://docs.python.org/3/library/collections.html#collections.UserList
import collections
# Data model reference documentation is also useful:
# https://docs.python.org/3/reference/datamodel.html#emulating-container-types
#
# Module for mathematical operations, used for angular properties.
# https://docs.python.org/3/library/math.html
from math import fmod, pi, isclose
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Vector, Quaternion
#
# Local imports, would go here.

class UpdateList(collections.UserList):
    def __init__(self, update, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update = update
        
    def __setitem__(self, index, value):
        list.__setitem__(self.data, index, value)
        self._update()

class Cursor(object):
    #
    # Handy constants
    zAxis = Vector((0,0,1))
    
    
    faceVectors = (
        (0, 0, 1),
        (0, 1, 0),
        (1, 0, 0),
        (0, 0, -1),
        (0, -1, 0),
        (-1, 0, 0)
    )
    faceCount = len(faceVectors)
    
    
    #
    # Infrastructure properties and methods.
    #
    @property
    def subjectPath(self):
        return self._subjectPath
    @subjectPath.setter
    def subjectPath(self, subjectPath):
        self._subjectPath = subjectPath
        self._update(True)
    #
    @property
    def restInterface(self):
        return self._restInterface
    @restInterface.setter
    def restInterface(self, restInterface):
        self._restInterface = restInterface
        self._update(True)
    #
    @property
    def add_visualiser(self):
        return self._add_visualiser
    @add_visualiser.setter
    def add_visualiser(self, add_visualiser):
        self._add_visualiser = add_visualiser
        self._update(False)
    #
    @property
    def add_empty(self):
        return self._add_empty
    @add_empty.setter
    def add_empty(self, add_empty):
        self._add_empty = add_empty
        self._update(False)
    @property
    #
    def visible(self):
        return self._visible
    @visible.setter
    def visible(self, visible):
        self._visible = visible
        self._update(False)
    #
    # Properties that define the cursor.
    #
    @property
    def origin(self):
        return self._origin
    @origin.setter
    def origin(self, origin):
        self._origin = origin
        self._update(False)
    @property
    def face(self):
        return self._face
    @face.setter
    def face(self, face):
        self._face = face
        self._update(False)
    # @property
    # def axis(self):
    #     return self._axis
    # @axis.setter
    # def axis(self, axis):
    #     self._axis = axis
    #     self._update(False)
    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, offset):
        self._offset = offset if offset is None or offset > 0.0 else 0.0
        self._update(False)
    @property
    def length(self):
        return self._length
    @length.setter
    def length(self, length):
        self._length = length if length is None or length > 0.0 else 0.0
        self._update(False)
    @property
    def radius(self):
        return self._radius
    @radius.setter
    def radius(self, radius):
        self._radius = radius if radius is None or radius > 0.0 else 0.0
        # if self._radius is not None:
        #     self._radiusVector = Vector((self._radius, 0, 0))
        self._update(False)
    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, rotation):
        # fmod on the next line allows negative values.
        self._rotation = fmod(rotation, pi * 2.0)
        self._update(False)
    #
    # Helper properties, read-only and based on the subject plus an offset from
    # cache. The offset is updated by setting other properties.
    #
    @property
    def base(self):
        return self._get_helper(0)
    @property
    def start(self):
        return self._get_helper(1)
    @property
    def end(self):
        return self._get_helper(2)
    @property
    def point(self):
        return self._get_helper(3)
    #
    def _get_helper(self, index):
        if self._helpers is None:
            return None
        return self._helpers[index].worldPosition.copy()
        
    def _update(self, changedSubject=False):
        if changedSubject:
            self._subject = None

        if (self._subject is None
            and self._subjectPath is not None
            and self._restInterface is not None
        ):
            self._subject = self._restInterface.rest_get(self.subjectPath)

        subject = self._subject
        if subject is None:
            return None
        #
        # Set the offset properties.
        axis = get_face_vector(self._face)


        normalised = Vector(self.axis).normalized()
        print(self.axis, normalised)
        axisVector = subject.getAxisVect(normalised)


        #
        # Parameter to getAxisVect is a list, from which it returns a Vector.
        self._baseOffset = subject.getAxisVect(self.origin)
        # print(self._origin, self._baseOffset)
        if self._baseOffset is None:
            self._startOffset = None
        else:
            self._startOffset = self._baseOffset.copy()
            if self._offset is not None:
                self._startOffset += self._offset * axisVector
        if self._startOffset is None:
            self._endOffset = None
        else:
            self._endOffset = self._startOffset.copy()
            if self._length is not None:
                self._endOffset += self._length * axisVector
        if self._endOffset is None:
            self._pointOffset = None
        else:
            self._pointOffset = self._endOffset.copy()
            if self._radius is not None:
                quaternion = Quaternion(
                    axisVector
                    , 0.0 if self._rotation is None else self._rotation)
                rotationVector = self._radiusVector.copy()
                rotationVector.rotate(quaternion)
                self._pointOffset += rotationVector
        #
        # Create the helper objects, if they don't exist and can be created now.
        created = False
        if self._helpers is None and self.add_empty is not None:
            created = True
            self._helpers = tuple(self._add_empty() for _ in range(4))
        if self._helpers is not None and (changedSubject or created):
            for helper in self._helpers:
                helper.set_parent(subject.tether)
        #
        # Position the helper objects.
        if self._helpers is not None:
            offsets = (self._baseOffset, self._startOffset, self._endOffset,
                       self._pointOffset)
            for index, helper in enumerate(self._helpers):
                worldPosition = subject.worldPosition.copy()
                if offsets[index] is not None:
                    worldPosition += offsets[index]
                helper.worldPosition = worldPosition

        if self._visible:
            created = False
            vectorPoints = (subject.worldPosition.copy(), self.base,
                            self.end, self.point, self.start)
            if self._visualisers is None and self._add_visualiser is not None:
                self._visualisers = tuple(self._add_visualiser()
                                          for _ in range(len(vectorPoints) - 1))
                created = True

            if self._visualisers is not None and (changedSubject or created):
                for visualiser in self._visualisers:
                    visualiser.set_parent(subject.tether)

            if self._visualisers is not None:
                for index, visualiser in enumerate(self._visualisers):
                    visualiser.make_vector(vectorPoints[index]
                                           , vectorPoints[index + 1])

    def get_face_vector(self, face):
        faceMod = fmod(face, self.faceCount)
        if faceMod < 0.0:
            faceMod += self.faceCount
        index0 = int(floor(faceMod))
        index1 = (index0 + 1) % self.faceCount
        vector0 = self.faceVectors[index0]
        vector1 = self.faceVectors[index1]
        factor = faceMod - float(index0)
        return tuple(
            value0 + factor * (vector1[index] - value0)
            for index, value0 in enumerate(vector0)
        )

    def __init__(self):
        self._subject = None
        self._visualisers = None
        self._helpers = None

        self._subjectPath = None
        self._restInterface = None
        self._add_visualiser = None
        self._add_empty = None
        self._visible = False

        self._origin = UpdateList(self._update, (0.0, 0.0, 0.0))
        # self._axis = UpdateList(self._update, (0.0, 0.0, 1.0))
        self._face = 0.0
        self._offset = None
        self._length = None
        self._radius = None
        self._rotation = None

        self._radiusVector = None
        self._originOffset = None
        self._startOffset = None
        self._endOffset = None
        self._pointOffset = None
