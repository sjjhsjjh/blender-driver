#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for use with Blender Game Engine.

Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Blender library imports, in alphabetic order.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Vector, Quaternion

class Cursor(object):
    #
    # Handy constants
    zAxis = Vector((0,0,1))
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
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, offset):
        self._offset = offset
        self._update(False)
    #
    @property
    def length(self):
        return self._length
    @length.setter
    def length(self, length):
        self._length = length
        self._update(False)
    #
    @property
    def radius(self):
        return self._radius
    @radius.setter
    def radius(self, radius):
        self._radius = radius
        if radius is not None:
            self._radiusVector = Vector((radius, 0, 0))
        self._update(False)
    #
    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self._update(False)
    #
    # Helper properties, read-only and based on the subject plus an offset from
    # cache. The offset is updated by setting other properties.
    #
    @property
    def origin(self):
        return self._get_helper(0)
    @property
    def end(self):
        return self._get_helper(1)
    @property
    def point(self):
        return self._get_helper(2)
    #
    def _get_helper(self, index):
        if self._helpers is None:
            return None
        return self._helpers[index].worldPosition.copy()
        
    def _update(self, changedSubject):
        if changedSubject:
            self._subject = None

        if (self._subject is None
            and self._subjectPath is not None
            and self._restInterface is not None
            ):
            self._subject = self.restInterface.rest_get(self.subjectPath)

        subject = self._subject
        if subject is None:
            return None
        #
        # Set the offset properties.
        axisVector = subject.getAxisVect(self.zAxis)
        self._originOffset = (
            None if self._offset is None else self._offset * axisVector)
        if self._originOffset is None:
            self._endOffset = None
        else:
            self._endOffset = self._originOffset.copy()
            if self._length is not None:
                self._endOffset += self._length * axisVector
        if self._endOffset is None:
            self._pointOffset = None
        else:
            self._pointOffset = self._endOffset.copy()
            if self._radius is not None:
                if self._rotation is None:
                    self._pointOffset += subject.getAxisVect(self._radiusVector)
                else:
                    quaternion = Quaternion(self.zAxis, self._rotation)
                    rotationVector = self._radiusVector.copy()
                    rotationVector.rotate(quaternion)
                    self._pointOffset += subject.getAxisVect(rotationVector)
        #
        # Create the helper objects, if they don't exist and can be created now.
        created = False
        if self._helpers is None and self.add_empty is not None:
            created = True
            self._helpers = tuple(self._add_empty() for _ in range(3))
        if self._helpers is not None and (changedSubject or created):
            for helper in self._helpers:
                helper.setParent(subject.tether)
        #
        # Position the helper objects.
        if self._helpers is not None:
            offsets = (self._originOffset, self._endOffset, self._pointOffset)
            for index, helper in enumerate(self._helpers):
                worldPosition = subject.worldPosition.copy()
                if offsets[index] is not None:
                    worldPosition += offsets[index]
                helper.worldPosition = worldPosition

        if self._visible:
            created = False
            if self._visualisers is None and self._add_visualiser is not None:
                self._visualisers = tuple(
                    self._add_visualiser() for _ in range(3))
                created = True

            if self._visualisers is not None and (changedSubject or created):
                for visualiser in self._visualisers:
                    visualiser.setParent(subject.tether)

            if self._visualisers is not None:
                self._visualisers[0].make_vector(self.origin, self.end)
                self._visualisers[1].make_vector(self.end, self.point)
                self._visualisers[2].make_vector(self.point, self.origin)

        # ToDo: End the visualisers if not visible, and set self._visualisers = None.

    def __init__(self):
        self._subject = None
        self._visualisers = None
        self._helpers = None

        self._subjectPath = None
        self._restInterface = None
        self._add_visualiser = None
        self._add_empty = None
        self._visible = False

        self._offset = None
        self._length = None
        self._radius = None
        self._rotation = None

        self._radiusVector = None
        self._originOffset = None
        self._endOffset = None
        self._pointOffset = None
