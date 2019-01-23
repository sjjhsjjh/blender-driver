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
# Module for mathematical operations, used for angular properties and face
# vector interpolation.
# https://docs.python.org/3/library/math.html
from math import fmod, pi, isclose, floor, radians
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine maths utilities.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
# They're super-effective!
from mathutils import Vector, Quaternion
#
# Local imports.
#
# Simplified rotation wrapper.
from .rotation import Rotation

class UpdateList(collections.UserList):
    def __init__(self, update, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update = update
        
    def __setitem__(self, index, value):
        list.__setitem__(self.data, index, value)
        self._update()

class Cursor(object):
    #
    # Constants.
    _axisBase = Vector((0, 0, 1))
    _radiusBase = Vector((1, 0, 0))
    _eulerOrders = ('YZX', 'ZXY', 'XYZ')
    #
    # Infrastructure properties and methods.
    @property
    def subjectPath(self):
        return self._subjectPath
    @subjectPath.setter
    def subjectPath(self, subjectPath):
        self._subjectPath = subjectPath
        self._update(True)
    #
    @property
    def selfPath(self):
        return self._selfPath
    @selfPath.setter
    def selfPath(self, selfPath):
        self._selfPath = tuple(selfPath[:])
        self._set_faces()
        self._check_faces()
    #
    @property
    def restInterface(self):
        return self._restInterface
    @restInterface.setter
    def restInterface(self, restInterface):
        self._restInterface = restInterface
        restInterface.check = self._check_faces
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
    @property
    def beingAnimated(self):
        return self._beingAnimated
    @beingAnimated.setter
    def beingAnimated(self, beingAnimated):
        wasAnimated = self._beingAnimated
        if beingAnimated and not wasAnimated:
            self._check_faces("Cursor animation start.")
        elif wasAnimated and not beingAnimated:
            if self._axis is not None:
                del self._axis[:]
            self._check_faces("Cursor animation stop.")
        self._beingAnimated = beingAnimated
    #
    # Properties that define the cursor.
    #
    @property
    def origin(self):
        '''Vector from the centre of the subject to the Cursor base.'''
        return self._origin
    @origin.setter
    def origin(self, origin):
        self._origin = origin
        self._update(False)
        
    @property
    def axis(self):
        '''Direction of the Cursor axis.'''
        return self._axis
    @axis.setter
    def axis(self, axis):
        self._check_faces("before axis set", axis)
        if axis is None:
            # This allows a REST put of None to relinquish control of
            # rotation.
            del self._axis[:]
        else:
            self._axis[:] = tuple(axis)
        self._check_faces("after axis set", axis)
    @axis.deleter
    def axis(self):
        self._check_faces("before axis delete")
        del self._axis[:]
        self._check_faces("after axis delete")
    
    # Accessors for the Rotation instance in self.axis
    def _get_axis_orientation(self):
        self._check_faces("_get_axis_orientation")
        return self._axisOrientation.copy()
    def _set_axis_orientation(self, orientation):
        self._axisOrientation = orientation
        self._check_faces("before update", orientation)
        self._update(False)
        self._check_faces("after update", orientation)

    @property
    def offset(self):
        '''Distance from the Cursor base to the start.'''
        return self._offset
    @offset.setter
    def offset(self, offset):
        self._offset = offset if offset is None or offset > 0.0 else 0.0
        self._update(False)
    @property
    def length(self):
        '''Distance from the Cursor start to the end.'''
        return self._length
    @length.setter
    def length(self, length):
        self._length = length if length is None or length > 0.0 else 0.0
        self._update(False)
    @property
    def radius(self):
        '''Distance from the Cursor end to the point.'''
        return self._radius
    @radius.setter
    def radius(self, radius):
        self._radius = radius if radius is None or radius > 0.0 else 0.0
        self._update(False)
    @property
    def rotation(self):
        '''Angle of the Cursor radius.'''
        return self._rotation
    @rotation.setter
    def rotation(self, rotation):
        # fmod on the next line allows negative values.
        self._rotation = fmod(rotation, pi * 2.0)
        self._update(False)
    @property
    def visualiserCalibre(self):
        return self._visualiserCalibre
    @visualiserCalibre.setter
    def visualiserCalibre(self, calibre):
        self._visualiserCalibre = calibre
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
    #
    # Special getters.
    #
    @property
    def moves(self):
        self._check_faces('moves getter', 0)
        return_ = tuple(self._get_face().moves[:])
        self._check_faces('moves getter', 1)
        return return_
    
    @property
    def normal(self):
        return self._get_face().normal
        
    def _get_face(self):
        # Work out which face best represents the current axis, by calculating
        # the angle between each and the axis vector as it would be in local
        # space.
        
        # If _faces isn't set, there isn't a subject yet so this method is
        # meaningless.
        if self._faces is None:
            return None
        
        lowest = None
        lowestIndex = None
        axisLocal = self._apply_axis_rotation(self._axisBase.copy())
        for index, face in enumerate(self._faces):
            angle = face.normalVector.angle(axisLocal);
            if lowest is None or angle < lowest:
                lowest = angle
                lowestIndex = index

        return self._faces[lowestIndex]

    # Empty class to hold face configuration.
    class _Empty:
        pass
    def _set_faces(self):
        faces = []
        for dimension in (1, 2, 0):
            for faceSign in (1, -1):
                face = self._Empty()
                face.dimension = dimension
                face.sign = faceSign
                face.normal = tuple(
                    faceSign if inner == dimension else 0 for inner in range(3))
                face.normalVector = Vector(face.normal)

                # The four options are radians(90) and radians(-90) in each of
                # the dimensions that have zero in the face vector.
                #
                # For efficiency, should update the required properties in the
                # axis setter. They are:
                # -   face as an index maybe.
                # -   tuple of 4 elements, one for each option.
                #
                # Maybe it isn't more efficient, because the axis setter gets
                # called all the time by the animation. The option getter only
                # gets called when an axis rotation is selected in the UI.

                moves = []
                for axisIndex, axisValue in enumerate(face.normal):
                    if axisValue != 0:
                        continue
                    for moveSign in (1, -1):
                        moves.append({
                            "preparation": {
                                "path":
                                    tuple(self.selfPath[:])
                                    + ('axis', 'order'),
                                "value": self._eulerOrders[axisIndex]
                            },
                            "animation": {
                                "subjectPath": tuple(self.selfPath[:]),
                                "valuePath":
                                    tuple(self.selfPath[:])
                                    + ('axis', axisIndex),
                                "delta": radians(90.0 * moveSign)
                            }
                        })
                face.moves = tuple(moves)
                faces.append(face)
        self._faces = tuple(faces)
    
    def _check_faces(self, *args):
        if self._faces is None:
            return
        exceptions = []
        for checkFaceIndex, checkFace in enumerate(self._faces):
            faceNormal = checkFace.normal
            for move in checkFace.moves:
                lastPath = move['animation']['valuePath'][-1]
                if faceNormal[lastPath] != 0:
                    exceptions.append(
                        'Wrong move at {} in [{}] {} d:{} s:{} {}'.format(
                            args, checkFaceIndex, faceNormal
                            , checkFace.dimension, checkFace.sign, move))
        if len(exceptions) > 0:
            raise RuntimeError("\n".join(exceptions))
    
    @property
    def facesOK(self):
        self._check_faces('facesOK')
        return True

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
        
        if self._axisOrientation is None:
            # Not sure of the correct maths for generating an identity matrix
            # that is 3x3. The matrix has to be 3x3 in order to call its
            # rotate() method. So, the code gets a suitable matrix by copying
            # one from the subject, which will be a KXGameObject.
            self._axisOrientation = subject.worldOrientation.copy()
            self._axisOrientation.identity()
            self._axis = Rotation(
                self._get_axis_orientation, self._set_axis_orientation)

        if (not self._loadedGenericStore
            and self._faces is not None
            and self._restInterface is not None
        ):
            self._restInterface.load_generic(
                self._faces[0].moves, self.selfPath + ('moves',))
            self._restInterface.load_generic(
                self._faces[0].normal, self.selfPath + ('normal',))
            self._loadedGenericStore = True
        #
        # Set the offset properties.
        #
        axisVector = subject.getAxisVect(
            self._apply_axis_rotation(self._axisBase.copy()))
        if self._radius is not None:
            radiusVector = subject.getAxisVect(
                self._apply_axis_rotation(self._radiusBase * self._radius))
        #
        # Parameter to getAxisVect is a list, from which it returns a Vector.
        self._baseOffset = subject.getAxisVect(self.origin)
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
                rotationVector = radiusVector
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
                if subject.tether is None:
                    subject.tether = self.add_empty()
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
                    if subject.tether is None:
                        subject.tether = self.add_empty()
                    visualiser.set_parent(subject.tether)

            if self._visualisers is not None:
                for index, visualiser in enumerate(self._visualisers):
                    visualiser.make_vector(vectorPoints[index]
                                           , vectorPoints[index + 1]
                                           , self.visualiserCalibre)

    def _apply_axis_rotation(self, vector):
        vector.rotate(self._axisOrientation)
        return vector

    # def get_face_vector(self, face):
    #     faceMod = fmod(face, self.faceCount)
    #     if faceMod < 0.0:
    #         faceMod += self.faceCount
    #     index0 = int(floor(faceMod))
    #     index1 = (index0 + 1) % self.faceCount
    #     vector0 = self.faceVectors[index0]
    #     vector1 = self.faceVectors[index1]
    #     factor = faceMod - float(index0)
    #     return tuple(
    #         value0 + factor * (vector1[index] - value0)
    #         for index, value0 in enumerate(vector0)
    #     )

    def __init__(self):
        self._subject = None
        self._visualisers = None
        self._faces = None
        self._helpers = None
        self._loadedGenericStore = False

        self._selfPath = None
        self._beingAnimated = False
        self._subjectPath = None
        self._restInterface = None
        self._add_visualiser = None
        self._add_empty = None
        self._visible = False

        self._origin = UpdateList(self._update, (0.0, 0.0, 0.0))
        # ToDo: Make it apply fmod to its items.
        self._axisOrientation = None
        self._axis = None
        
        self._offset = None
        self._length = None
        self._radius = None
        self._rotation = None
        self._visualiserCalibre = None

        self._originOffset = None
        self._startOffset = None
        self._endOffset = None
        self._pointOffset = None
