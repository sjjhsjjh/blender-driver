#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for use with Blender Game Engine.

Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order, would go here.
#
# Blender library imports, in alphabetic order.
#
# Blender Game Engine KX_GameObject
# https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html
# Can't be imported here because this module gets imported in the bpy context
# too, in which bge isn't available.
#
# Local imports.
#
# RESTful interface.
# from rest import RestInterface
#
# Custom property for access to immutable properties in KX_GameObject.
from path_store.hosted import InterceptProperty
#
# Simplified rotation wrapper.
from .rotation import Rotation

def get_game_object_subclass(bge):
    """\
    Get a custom subclass of of KX_GameObject in which the Vector properties are
    mutable at the item level. For example:
    
        gameObject.worldScale[2] = 2.5 # Where 2.5 is the desired Y scale.
    
    This is a function so that this file can be imported outside the context of
    Blender Game Engine. Pass as a parameter a reference to the bge module.
    """
    
    KX_GameObject = bge.types.KX_GameObject
    
    class GameObject(KX_GameObject):
        """\
        Subclass with intercept properties for worldScale, worldPosition, and in
        future other array properties whose elements are immutable in the base
        class.
        """
        @InterceptProperty()
        def worldScale(self):
            return super().worldScale
        @worldScale.intercept_getter
        def worldScale(self):
            return self._worldScale
        @worldScale.intercept_setter
        def worldScale(self, value):
            self._worldScale = value
        @worldScale.destination_setter
        def worldScale(self, value):
            # It'd be nice to do this:
            #
            #     super(self).worldScale = value
            #
            # But see this issue: http://bugs.python.org/issue14965
            # So instead, we have the following.
            KX_GameObject.worldScale.__set__(self, value)
    
        @InterceptProperty()
        def worldPosition(self):
            return super().worldPosition
        @worldPosition.intercept_getter
        def worldPosition(self):
            return self._worldPosition
        @worldPosition.intercept_setter
        def worldPosition(self, value):
            self._worldPosition = value
        @worldPosition.destination_setter
        def worldPosition(self, value):
            KX_GameObject.worldPosition.__set__(self, value)

        @property
        def tether(self):
            return self._tether
        @tether.setter
        def tether(self, tether):
            if self._tether is not None and self._tether is not tether:
                children = len(self.tether.children)
                if children > 0:
                    raise RuntimeError("Tether endObject when it has"
                                       " children:{}.".format(children))
                self._tether.endObject()
            self._tether = tether
            self.update()
            
        def update(self):
            if self.tether is not None:
                self.tether.worldPosition = self.worldPosition.copy()
                self.tether.worldOrientation = self.worldOrientation.copy()
        
        @property
        def physics(self):
            return not self.isSuspendDynamics
        @physics.setter
        def physics(self, physics):
            if physics:
                # Clear the rotation. An object that has physics could collide
                # with another object and then tumble. This means that any user
                # has lost control of the object's rotation.
                del self.rotation[:]
                self.restoreDynamics()
            else:
                self.suspendDynamics(True)
        
        # There can be multiple current animations on an object, which could
        # complete at different times.
        #
        # When the first animation is applied to an object, its physics must be
        # suspended.
        # When the last animation on an object has completed, its physics must
        # be resumed.

        @property
        def beingAnimated(self):
            return self._beingAnimated
        @beingAnimated.setter
        def beingAnimated(self, beingAnimated):
            wasAnimated = self._beingAnimated
            if beingAnimated and not wasAnimated:
                self.physics = False
            elif wasAnimated and not beingAnimated:
                # Next line causes the rotation array to be cleared.
                self.physics = True
            self._beingAnimated = beingAnimated

        @property
        def rotation(self):
            return self._rotation
        @rotation.setter
        def rotation(self, rotation):
            if rotation is None:
                # This allows a REST put of None to relinquish control of
                # rotation.
                del self._rotation[:]
            else:
                self._rotation[:] = tuple(rotation)
        @rotation.deleter
        def rotation(self):
            del self._rotation[:]

        def _get_orientation(self):
            return self.worldOrientation
        def _set_orientation(self, worldOrientation):
            self.worldOrientation = worldOrientation
        
        # Override.
        def endObject(self):
            # Next line causes the tether property setter, above, to run. That
            # in turn will endObject the tether, if there is one. That comes
            # back through here, because the tether is also an instance of this
            # GameObject. That's OK if tethers don't get tethers.
            self.tether = None
            super().endObject()

        def set_parent(self, parent):
            if parent is None:
                self.removeParent()
            else:
                self.setParent(parent)
        # It'd be nice to do the above with some clever Python property code
        # maybe like this:
        #
        #     parent = property(KX_GameObject.parent.fget, _set_parent)
        #
        # It doesn't seem to work, maybe because parent isn't a normal Python
        # property. Instead, there's a setter method. The name follows the PEP 8
        # convention, which makes it different to KX_GameObject.setParent.
        # This single setter is a convenience. Native setParent(None) seems to
        # be a no-op, instead of removing the parent.
        
        def make_vector(self, startVector, endVector, calibre=0.1):
            vector = endVector - startVector
            if vector.magnitude == 0.0:
                self.worldScale = (calibre, calibre, calibre)
            else:
                self.worldScale = (calibre, calibre, vector.magnitude/2.0)
            self.worldPosition = startVector + vector/2.0
            if vector.magnitude != 0.0:
                self.alignAxisToVect(vector)

        def __init__(self, oldOwner):
            self._rotation = Rotation(
                self._get_orientation, self._set_orientation)
            
            self._tether = None
            self._beingAnimated = False

    return GameObject
        
def get_game_text_subclass(bge, GameObject):
    """\
    Get a custom subclass of of KX_FontObject with similar characteristics to
    the KX_GameObject subclass returned by get_game_object_subclass().
    
    This is a function so that this file can be imported outside the context of
    Blender Game Engine. Pass as parameters:
    
    -   A reference to the bge module.
    -   The subclass returned by a previous call to get_game_object_subclass().
    """
    
    class GameText(bge.types.KX_FontObject, GameObject):
        pass

    # KX_FontObject is a very light subclass of KX_GameObject. It seems like it
    # should be possible to instiate a KX_GameObject subclass from an existing
    # KX_FontObject instance, but it isn't allowed. The existing KX_FontObject
    # instance must be passed to a KX_FontObject subclass.
    # The above declaration uses multiple inhertance to give the KX_FontObject
    # subclass all the extra methods in the KX_GameObject subclass without any
    # code.
    
    return GameText
