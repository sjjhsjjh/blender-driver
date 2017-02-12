#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Utility layer on the main Blender Python programming interface. This isn't
the utilities for the Blender Game Engine.

This module can only be used from within Blender."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for JavaScript Object Notation (JSON) strings.
import json
#
# Blender library imports, in alphabetic order.
#
# These modules can only be imported if running from within Blender.
try:
    #
    # Main Blender Python interface.
    
    import bpy
    #
    # Vectors.
    from mathutils import Vector
except ImportError as error:
    print(__doc__)
    print(error)

def load_driver(driverClass, arguments):
    """Load the owner data subclass and initialise everything.

This subroutine has all the hard-coded names.

This is the end of the chain from:

-   The blenderdriver.py script, which launches Blender and specifies the \
    .blend file to open and tells Blender to run the launch_blender_driver.py \
    script.
-   The launch_blender_driver.py script, which works out the name of the \
    driver application module, extends the Python module path, and then calls \
    this function.

The driver application class is instantiated in two different stages: Data and \
Game. The Data stage is here. The Game class is when the Blender Game Engine \
starts."""
    if arguments.verbose:
        print('load_driver begin.', arguments, __package__)
    #
    # Add and configure the driver gateway object, on which everything else will
    # depend. It is a Blender Empty.
    driverGateway = set_up_object(arguments.gateway)
    #
    # Create the settings collection. The settings include:
    # -   The module path and name of the application class.
    # -   The arguments from the command line.
    # -   The Blender version string, so that it can be retrieved in the BGE
    #     stage.
    settings = {'module': driverClass.__module__,
                'class': driverClass.__name__,
                'arguments': None if arguments is None else vars(arguments),
                'blender': bpy.app.version_string[:] }
    #
    # Instantiate the application class.
    driver = driverClass(settings)
    #
    # Call the application's constructor for the Blender data stage. Pass it a
    # reference to the scene and the driver gateway. This is a data scene, not a
    # game scene. For now, assume there is only a single scene.
    driver.data_constructor(bpy.data.scenes[0], driverGateway)
    #
    # Call the override-able initialisation.
    driver.data_initialise()
    #
    # Attach the controllers for BGE to the gateway object.
    controllersPackage = __package__
    if arguments.controllersPackage is not None:
        controllersPackage = arguments.controllersPackage
    controllers = get_controllers(
            driver, controllersPackage, arguments.controllersModule,
            ('initialise', 'tick', 'keyboard'))
    if arguments.verbose:
        print('load_driver', 'controllers', vars(controllers))
    configure_gateway(driverGateway, controllers)
    #
    # Put a collection of configuration settings into one or more game
    # properties. The collection gets read from there by the
    # blender_driver.controllers initialise() subroutine when the Blender game
    # engine is started.
    set_game_property(driverGateway, 'settingsJSON', json.dumps(settings) )
    #
    # Start the Blender Game Engine, if that was specified.
    # Could also have an option to export as a blender game here.
    if arguments.start:
        if arguments.verbose:
            print('load_driver starting BGE.')
        bpy.ops.view3d.game_start()
    if arguments.verbose:
        print('load_driver end.')

def set_up_object(name, params={}):
    """Set up an object in the data layer. Returns a reference to the object."""
    object_ = None
    objectIndex = bpy.data.objects.find(name)
    if objectIndex >= 0:
        object_ = bpy.data.objects[objectIndex]
    new_ = (object_ is None)
    #
    # Create a new object with the specified Blender mesh, if necessary.
    subtype = params.get('subtype')
    if new_:
        if subtype is None or subtype == 'Empty':
            object_ = bpy.data.objects.new(name, None)
        elif subtype == 'Text':
            #
            # Text objects are added in a different way, ops not data, which
            # happens to select them when they're added, and adds them to the
            # scene.
            bpy.ops.object.text_add()
            object_ = bpy.data.objects[-1]
            #
            # Text objects always need a Text game property, to hold the text
            # that they display.
            bpy.ops.object.game_property_new(type='STRING', name='Text')
            #
            # The different way of adding doesn't set the object name, so set it
            # here.
            object_.name = name
            # This would be the data way, but it seems to create a different
            # type of thing.
            # object_ = bpy.data.texts.new(name)
        else:
            object_ = bpy.data.objects.new(name, bpy.data.meshes[subtype])
    #
    # Set its physics type and related attributes.
    physicsType = params.get('physicsType')
    if physicsType is None and new_:
        if subtype is None:
            physicsType = 'NO_COLLISION'
        else:
            physicsType = 'RIGID_BODY'
    if physicsType is not None:
        object_.game.physics_type = physicsType
        if physicsType != 'NO_COLLISION':
            object_.game.use_collision_bounds = True
    #
    # Position the object, if necessary.
    location = params.get('location')
    if location is not None:
        object_.location = Vector(location)
    #
    # Scale the object, if necessary.
    dimensions = params.get('dimensions')
    if dimensions is not None:
        # object_.dimensions = Vector(dimensions)
        object_.scale = Vector(dimensions)
    #
    # Add the object to the current scene, if necessary.
    if new_ and subtype != 'Text':
        bpy.context.scene.objects.link(object_)
    #
    # Set its Blender ghost, if specified.
    ghost = params.get('ghost')
    if ghost is not None:
        object_.game.use_ghost = ghost
    #
    # Add the object to the required layers.
    #
    # The gateway object, which has subtype None, goes on every layer.
    # Template objects go on layer one only. This means that:
    #
    # -   Template objects aren't visible by default.
    # -   Template objects can be addObject'd later, by bge.
    # -   The module that contains the controllers of the gateway object always
    #     gets imported, whatever layer happens to be active when BGE gets
    #     started.
    layer = 1
    if subtype is None:
        layer = 0
    #
    # It seems that Blender doesn't allow an object to be on no layers at any
    # time. This makes the following line necessary, in addition to the for
    # loop.
    object_.layers[layer] = True
    for index in range(len(object_.layers)):
        if index != layer:
            object_.layers[index] = (subtype is None)
    #
    # Refresh the current scene.
    bpy.context.scene.update()
    #
    # Return a reference to the object.
    return object_

def get_controllers(driver, packageName, moduleName, controllers):
    """Get the names of the specified controllers that exist in the specified
    module and package. Names of controllers are returned in a namespace type of
    object, in a package.module.controller format. The application can remove
    any, for diagnostic purposes."""
    #
    # Declare an empty class to use as a namespace.
    # https://docs.python.org/3.5/tutorial/classes.html#odds-and-ends
    class Controllers:
        pass
    return_ = Controllers()
    #
    # Start by adding all of them.
    for controller in controllers:
        setattr(return_, controller, ".".join(
            (packageName, moduleName, controller)))
    #
    # Give the application an opportunity to remove any, for diagnostic
    # purposes.
    driver.diagnostic_remove_controllers(return_)
    return return_

def configure_gateway(driver, controllers):
    """Set various configurations that make the driver gateway work or are
    convenient."""
    #
    bpy.context.scene.render.engine = 'BLENDER_GAME'
    bpy.ops.wm.addon_enable(module="game_engine_save_as_runtime")
    #
    # Controller and sensor for initialisation.
    if controllers.initialise is not None:
        sensor = add_sensor(driver, controllers.initialise)
    #
    # Controller and sensor for every tick.
    if controllers.tick is not None:
        sensor = add_sensor(driver, controllers.tick)
        sensor.use_pulse_true_level = True
        #
        # Set the tick frequency using whatever API the current version of
        # Blender has.
        if hasattr(sensor, 'frequency'):
            sensor.frequency = 0
        else:
            sensor.tick_skip = 0
    #
    # Controller and sensor for the keyboard. This allows, for example, a back
    # door to be added to terminate the engine.
    if controllers.keyboard is not None:
        sensor = add_sensor(driver, controllers.keyboard, 'KEYBOARD')
        sensor.use_all_keys = True

def add_sensor(driver, subroutine, sensorType='ALWAYS'):
    select_only(driver)
    bpy.ops.logic.controller_add(type='PYTHON')
    #
    # Only way to access the controller just added is to get the last one now.
    controller = driver.game.controllers[-1]
    controller.mode = 'MODULE'
    controller.module = subroutine
    controller.name = subroutine
    bpy.ops.logic.sensor_add(type=sensorType)
    #
    # Only way to access the sensor just added is to get the last one now.
    sensor = driver.game.sensors[-1]
    sensor.name = subroutine
    sensor.use_tap = True
    sensor.link(controller)
    return sensor

def select_only(target):
    """Set the Blender user interface selection to a specified single object, or
    to nothing. If a single object is selected then it is also made active. Some
    parts of the programming interface also require that an object is
    selected."""
    bpy.ops.object.select_all(action='DESELECT')
    if target is not None:
        if isinstance(target, str):
            target = bpy.data.objects[target]
        target.select = True
        bpy.context.scene.objects.active = target
    return target

def set_up_objects(objectsDict):
    return_ = []
    if objectsDict is None:
        return return_
    for name in objectsDict.keys():
        return_.append(set_up_object(name, objectsDict[name]))
    return return_
    
def set_game_property(object_, key, value):
    """Set a game property in the data context, i.e. before the game engine has
    started."""
    select_only(object_)
    #
    # Attempt to add the value to a single property. This might not work.
    bpy.ops.object.game_property_new(type='STRING', name=key)
    #
    # Get a reference to the new game property.
    gameProperty = object_.game.properties[-1]
    #
    # Set the value, then check that it worked.
    gameProperty.value = value
    if gameProperty.value == value:
        return object_
    #
    # If this code is reached, then it didn't work.
    #
    # Confirm that it didn't work because the value is too long.
    if not value.startswith(gameProperty.value):
        # The set didn't work, and it isn't because the value is too long.
        # Fail now.
        raise AssertionError(''.join((
            'Game property value set failed. Expected "', value,
            '". Actual "', gameProperty.value, '"' )))
    #
    # The set didn't work because the value is too long. Split the value
    # across an "array" of game properties. Actually, a number of game
    # properties with a single root name and numeric suffixes.
    #
    # Find out the maximum length of a game property.
    max = len(gameProperty.value)
    #
    # Delete the property that failed to take the whole value.
    bpy.ops.object.game_property_remove(-1)
    #
    # Break the value into chunks and set each into a game property with a
    # key that has a suffix for its chunk number.
    chunks = int(len(value) / max) + 1
    index = 0
    for chunk in range(chunks):
        chunkValue = value[ index + max*chunk : index + max*(chunk+1) ]
        bpy.ops.object.game_property_new(type='STRING', name=key + str(chunk))
        chunkProperty = object_.game.properties[-1]
        chunkProperty.value = chunkValue

    return object_

def get_game_property(object_, key):
    """Get a property value from a game object in the game context, i.e. when
    the game engine is running."""
    properties = object_.getPropertyNames()
    if key in properties:
        # Property name on its own found. It contains the whole value.
        return object_[key]
            
    if ''.join((key, '0')) in properties:
        # Property name found with 0 appended. The value is split across a
        # number of properties. Concatenate them to retrieve the value.
        value = ''
        index = 0
        while True:
            chunkName = ''.join((key, str(index)))
            if chunkName not in properties:
                break
            value = ''.join((value, object_[chunkName]))
            index += 1
        return value

    raise AttributeError(''.join(('No game property for "', key, '"')))

def delete_except(keepers):
    # Following lines are a bit naughty. They add some meshes using the ops API.
    # This is only done in order to add the items to the project's meshes. The
    # next thing that happens is everything gets deleted, including the newly
    # added objects. The meshes are not deleted when the objects are deleted
    # though.
    # If we don't do this, then objects based on these meshes cannot be created
    # later.
    bpy.ops.mesh.primitive_uv_sphere_add()
    bpy.ops.mesh.primitive_circle_add()
    bpy.ops.mesh.primitive_torus_add()
    bpy.ops.mesh.primitive_cone_add()
    #
    # Delete everything except the keepers.
    #
    # Select all layers.
    for layer_index in range(len(bpy.data.scenes[0].layers)):
        bpy.data.scenes[0].layers[layer_index] = True
    #
    # Select all objects, on all layers.
    bpy.ops.object.select_all(action='SELECT')
    #
    # Unselect the keepers.
    if keepers is not None:
        for keeper in keepers:
            if isinstance(keeper, str):
                if keeper in bpy.data.objects:
                    bpy.data.objects[keeper].select = False
                else:
                    raise AttributeError(''.join((
                       'bpyutils delete_except "', keeper, '" not found.')))
            else:
                keeper.select = False
    #
    # And delete.
    bpy.ops.object.delete()
    #
    # Select only the first layer.
    for layer_index in range(len(bpy.data.scenes[0].layers)):
        if layer_index <= 0:
            bpy.data.scenes[0].layers[layer_index] = True
        else:
            bpy.data.scenes[0].layers[layer_index] = False
    #
    # Return None if there were no keepers.
    if keepers is None or len(keepers) < 1:
        return None
    #
    # Otherwise, select and return the first keeper.
    return select_only(keepers[0])

def set_active_layer(layer):
    # It'd nice to set the active layer here. There doesn't seem to be any way
    # to do that in Python. Second best is to terminate if it happens to have
    # the wrong value.
    #
    # for index in range(len(bpy.data.scenes[0].layers)):
    #     bpy.data.scenes[0].layers[index] = (index == 0)
    #     print( index, bpy.data.scenes[0].layers[index] )
    # bpy.data.scenes[0].layers[0] = True
    # print( "Active layer:", bpy.data.scenes[0].active_layer )
    # bpy.context.scene.update()
    activeLayer = bpy.data.scenes[0].active_layer
    if activeLayer != layer:
        raise RuntimeError("".join((
            "Active layer wrong. You have to set it manually, sorry.",
            " Required:", str(layer), ". Actual:", str(activeLayer), ".")))
