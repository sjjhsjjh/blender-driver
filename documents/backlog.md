Backlog
=======
-   Maybe label moves North, South, East, West.

-   Review how the generic store is set up. Maybe it should all be done by walk,
    like the load_generic method does. Maybe the _generic_value subroutine
    should be got rid of.

-   Covert radians to degrees in NumericPanel. Create animations with modulus
    for angular ones.

-   Maybe automatically load read-only properties into the generic store.

-   Next video.

-   Show and hide Cursor instances, by starting and ending the visualisers.

    End the visualisers if not visible, and set self._visualisers = None.

-   Unit test for raising an error when the tether has children.

-   Non-linear animation speed. Maybe accelerating based on elapsed time, but
    decelerating based on proximity to target value.

-   Option for keyboard shortcuts in the browser, instead of clickless camera
    controls.

-   Maybe add a sweeper or something that ends any objects that have somehow
    escaped from the gameObjects array, unless they have children.

-   Unit tests for: Suppose a game object collection element, N, changes from a
    game object, O, to None. At that point, the BGE object that corresponds to N
    doesn't get endObject'd but it should.

-   Add support for wildcards in rest_patch to support commands like the
    following.
    
        PATCH /root/gameObjects/*
        {
            "physics": true
        }
    
    That would set physics to true in every item in the gameObjects collection.
    
-   Add support for getting array length, to support commands like the
    following.
    
        GET /root/gameObjects/length
    
    Where: gameObjects is an array and it returns the length of the array.
    
-   Lamps.

-   See about getting the launch script to start the browser, or at least
    refresh.

-   Read charset from content-type. Also check content-type in requests.

-   Add a unit test like TestGameObject test_rest_list.

-   Maybe have a structure in the AnimatedRestInterface like:

        'root'
          |
          +----'gameObjects'
                 |
                 + <name of template object, T>
                     |
                     + <collection of game objects>
                       Put'ing a dict here would create a KXGameObject based on
                       the object named T in the .blend file.

    -   Separate the game engine and path animation parts of
        AnimatedRestInterface, and move the game engine parts into the
        sub-directory.

-   Maybe change the thread application class to be like the unittest
    application:
    
    -   Spawn a small number of threads at the start, instead of one per tick.
    -   Use a barrier and other thread scheduling gubbins to share execution
        between them.

-   Move the classes out of the unittest application into a sub-directory, and
    move the unit tests themselves into a sub-sub-directory probably.

-   Uplift timing analysis to be a class, and to have an option for whether to
    retain the whole list or just increment on every record.

-   Add a unit test for Blender Python not having the subprocess.DEVNULL
    constant.

-   Check if suspend and restore Physics works and can be called on non-physics
    objects.

-   Unit test for InterceptProperty implementation of a mutable string.

-   Unit tests for InterceptProperty setattr.

-   Implement POST after thinking about what it should do. POST to an array
    could append to the array, easy.

    Could treat -1 as a special case if it is the path leg being used as an
    index into an array. If leg is -1, change leg to len(parent) so that the
    parent list or tuple gets extended by the point maker. However, this would
    be inconsistent with Python array indexing, in which a negative index is to
    be counted back from the end, e.g. -1 is the last element.

-   How to do applyImpulse? Maybe by POST to an "impulse" property, that gets
    pushed down to a setter, that executes the applyImpulse and discards its own
    value.

-   Move heavier diagnostic logs into unit tests in which Mock objects track
    calls.

-   Replace parts of the diagnostic server with unit tests.

License
=======
This file is:  

-   (c) 2018 Jim Hawkins.
-   MIT licensed, see https://opensource.org/licenses/MIT
-   Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
