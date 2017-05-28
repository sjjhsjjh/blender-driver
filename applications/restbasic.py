#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for Blender Driver demonstration application.

This code illustrates:

-   Basic use of the Blender Game Engine (BGE) KX_GameObject interface, to
    change the size of a game object.
-   Termination of BGE when any key is pressed.
-   Spawning a single thread at the start of BGE execution. The thread is
    joined before terminating BGE.
-   Use of a thread lock to indicate termination is due.

This application doesn't override the Blender Driver game_tick, which is then a
pass in the base class.

This module can only be used from within the Blender Game Engine."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for command line switches.
# https://docs.python.org/3.5/library/argparse.html
# The import isn't needed because this class uses the base class to get an
# object.
# import argparse
#
# This module uses the Thread class.
# https://docs.python.org/3.4/library/threading.html#thread-objects
import threading
#
# Module for sleep.
# https://docs.python.org/3.5/library/time.html
import time
#
# Third party modules, in alphabetic order.
#
# Blender library imports, in alphabetic order.
#
# Main Blender Python interface, which is used to get the size of a mesh.
# Import isn't needed because the base class keeps a reference to the interface
# object.
# import bpy
#
# Blender Game Engine KX_GameObject
# Import isn't needed because this class gets an object that has been created
# elsewhere.
# https://www.blender.org/api/blender_python_api_current/bge.types.KX_GameObject.html
#
# Blender Game Engine maths utilities, which can only be imported if running
# from within the Blender Game Engine.
# Import isn't needed because this class gets a Vector from the bpy layer.
# http://www.blender.org/api/blender_python_api_current/mathutils.html
#
# Local imports.
#
# Blender Driver application with threads and locks.
from . import demonstration

from path_store.rest import RestInterface

# Diagnostic print to show when it's imported. Only printed if all its own
# imports run OK.
print('"'.join(('Application module ', __name__, '.')))


class VectorSetter(list):
    
    def __setitem__(self, index, value):
        # print("VectorSetter setitem", index, value)
        vector = getattr(self._host, self._attr).copy()
        # vector = self._vector.copy()
        vector[index] = value
        setattr(self._host, self._attr, vector)
        # self._setter(vector)
        # self._vector[index] = value
    
    def set(self, value):
        setattr(self._host, self._attr, self._attrClass(value))
    
    def __init__(self, host, attr):
        self._host = host
        self._attr = attr
        self._attrClass = getattr(self._host, self._attr).__class__

# class HostedAttribute(object):



class HostedProperty(property):
    
    class HostHolder(object):
        
        def __getitem__(self, index):
            # print("HostHolder getitem", index)
            host = getattr(self._instance, self._hostName)
            attr = getattr(host, self._attrName)
            return attr[index]

        def __setitem__(self, index, value):
            # print("HostHolder setitem", index, value)
            # mutable = list(getattr(self.host, self._attr))
            host = getattr(self._instance, self._hostName)
            attr = getattr(host, self._attrName)
            mutable = list(attr)
            mutable[index] = value
            # setattr(self._host, self._attr, vector)
            # self.set(None, mutable)
            setattr(host, self._attrName, attr.__class__(mutable))
        
        def __init__(self, instance, hostName, attrName):
            self._instance = instance
            self._hostName = hostName
            self._attrName = attrName
    
    # @property
    # def host(self):
    #     return self._host
    # @host.setter
    # def host(self, host):
    #     self._host = host
    #     if host is not None:
    #         self._attrClass = getattr(self._host, self._attr).__class__

            
    # Getter for the host attribute goes here.


    def get(self, instance):
        # return getattr(getattr(instance, self._hostName), self._name)
        return getattr(instance, self._name)
        # return getattr(self.host, self._attr)
        # return self

    def set(self, instance, value):
        # if isinstance(value, tuple):
        #     host = value[0]
        #     value = value[1]
        # else:
        #     host = self._host
        # 
        # setattr(self._host, self._attr, self._attrClass(value))
        # return setattr(instance, self._name, value)
        #
        # Setting to None initialises the holder.
        print('HostedProperty setter', value)
        if value is None:
            hostHolder = self.HostHolder(instance, self._hostName, self._attr)
            setattr(instance, self._name, hostHolder)
        else:
            host = getattr(instance, self._hostName)
            attr = getattr(host, self._attr)
            # ToDo: Optimisation goes here.
            setattr(host, self._attr, attr.__class__(value))


    def delete(self, instance):
        delattr(instance, self._name)
    
    def __init__(self, attr, hostName, name=None):
        self._attr = attr
        self._name = '_' + attr if name is None else name
        self._hostName = hostName
        super().__init__(self.get, self.set, self.delete)

class Wrapper(object):
    @property
    def bgeObject(self):
        return self._bgeObject
    
    # @property
    # def worldScale(self):
    #     return self._worldScale
    # @worldScale.setter
    # def worldScale(self, worldScale):
    #     self._worldScale.set(worldScale)
    #     # self._bgeObject.worldScale = worldScale
    # # def setWorldScale(self, worldScale):
    # #     self.worldScale = worldScale
    
    worldScale = HostedProperty('worldScale', 'bgeObject')
    
    def __init__(self, bgeObject):
        self._bgeObject = bgeObject
        # self._worldScale = VectorSetter(
        #     self._bgeObject.worldScale, self.__class__.worldScale.fset)
        # self._worldScale = VectorSetter(self._bgeObject, 'worldScale')
        # self.worldScale = TupleProperty('worldScale')
        self.worldScale = None # TupleProperty('worldScale', self._bgeObject)
        # self.worldScale.host = self._bgeObject



class Application(demonstration.Application):
    
    # Overriden.
    def game_initialise(self):
        super().game_initialise()
        threading.Thread(
            target=self.pulse_object_scale, name="pulse_object_scale" ).start()
 
    def pulse_object_scale(self):
        """Pulse the scale of a game object for ever. Run as a thread."""
        minScale = self.arguments.minScale
        changeScale = self.arguments.changeScale
        increments = self.arguments.increments
        objectName = self.arguments.pulsar
        #
        # Get the underlying dimensions of the Blender mesh, from the data
        # layer. It's a mathutils.Vector instance.
        dimensions = tuple(self.bpy.data.objects[objectName].dimensions)
        #
        # Get a reference to the game object.
        object_ = Wrapper(self.gameScene.objects[objectName])
        
        objin = RestInterface()
        objin.verbose = self.arguments.verbose
        objin.rest_put(object_)
        
        
        while True:
            for cycle in range(3):
                for scale in range(increments):
                    self.verbosely(
                        __name__ , 'pulse_object_scale', "locking ...")
                    self.mainLock.acquire()
                    try:
                        self.verbosely(
                            __name__, 'pulse_object_scale', "locked.")

                        if self.terminating():
                            self.verbosely(
                                __name__, 'pulse_object_scale', "Stop.")
                            return
                        scales = (
                            minScale
                            + (changeScale * (scale + 1) / increments)
                            , minScale
                            + (changeScale * (increments - scale) / increments)
                            , minScale)
                        # worldScale = dimensions.copy()
                        worldScale = list(dimensions)
                        for index in range(3):
                            objin.rest_patch(
                                worldScale[index] * scales[(cycle+index)%3]
                                , ('worldScale', index))
                            # worldScale[index] *= scales[(cycle+index)%3]
                        # object_.worldScale = worldScale

                        # objin.rest_put(worldScale, 'worldScale')
                    finally:
                        self.verbosely(
                            __name__, 'pulse_object_scale', "releasing.")
                        self.mainLock.release()

                    if self.arguments.sleep is not None:
                        time.sleep(self.arguments.sleep)
    
    def game_keyboard(self, keyEvents):
        self.verbosely(__name__, 'game_keyboard', "Terminating.")
        self.game_terminate()
        
    def get_argument_parser(self):
        """Method that returns an ArgumentParser. Overriden."""
        parser = super().get_argument_parser()
        parser.prog = ".".join((__name__, self.__class__.__name__))
        parser.add_argument(
            '--increments', type=int, default=40, help=
            "Number of increments. Default: 40.")
        parser.add_argument(
            '--changeScale', type=float, default=2.0,
            help="Change of scale. Default: 2.0.")
        parser.add_argument(
            '--minScale', type=float, default=0.5,
            help="Minimum scale. Default: 0.5.")
        parser.add_argument(
            '--pulsar', default="Cube",
            help="Name of the object to pulse.")
        parser.add_argument(
            '--sleep', type=float, help=
            "Sleep after each increment, for a floating point number of"
            " seconds. Default is not to sleep.")
        return parser
