#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
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
# Import isn't needed because this class gets an object that has been created
# elsewhere.
# https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html

# Local imports.
#
# RESTful interface.
# from rest import RestInterface
#
# Custom property for access to immutable properties in KX_GameObject.
from path_store.hosted import HostedProperty



class GameObject(object):
    @property
    def bgeObject(self):
        return self._bgeObject
    
    bgeProperties = ('worldScale', 'worldPosition')
    # worldScale = HostedProperty('worldScale', 'bgeObject')
    # worldPosition = HostedProperty('worldPosition', 'bgeObject')
    
    def __init__(self, bgeObject):
        self._bgeObject = bgeObject
        # self.worldScale = None
        # self.worldPosition = None
        for bgeProperty in self.bgeProperties:
            setattr(self, bgeProperty, None)

for bgeProperty in GameObject.bgeProperties:
    setattr(GameObject, bgeProperty , HostedProperty(bgeProperty, 'bgeObject'))


# 
# 
# class RestBGEObject(RestInterface):
#     
#     def rest_POST(self, parameters):
#         # Add an object to the scene.
#         # Make the object instance be self.restPrincipal
#         # call super().restPOST(parameters) which will set each thing in the
#         # parameters dictionary.
#         pass
