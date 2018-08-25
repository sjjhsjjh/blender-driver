Backlog
=======
-   Next video:

    -   Demonstration User Interface.
    -   Control object creation from the browser.
    -   Control camera motion from the browser.
    -   Display a Fetch count in the browser.
    -   Put the results and Clear button in a fieldset.

-   Load the get_generic store by retrieving some things or in some other way at
    game_initialise.

-   Maybe add a sweeper or something that ends any objects that have somehow
    escaped from the gameObjects array.

-   Suppose a game object collection element, N, changes from a game object, O,
    to None. At that point, the BGE object that corresponds to N doesn't get
    endObject'd but it should.

-   Add support for wildcards in rest_patch to support commands like the
    following.
    
        PATCH /root/gameObject/*
        {
            "physics": true
        }
    
    That would set physics to true in every item in the gameObjects collection.

-   See about getting the launch script to start the browser, or at least
    refresh.

-   Unit tests for pathify_split.

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

-   Get a JSON representation of a path store principal.

-   HTTP server that responds to a GET request with a JSON representation of the
    path store.

-   Move heavier diagnostic logs into unit tests in which Mock objects track
    calls.

-   Replace parts of the diagnostic server with unit tests.

License
=======
This file is:  

-   (c) 2018 Jim Hawkins.
-   MIT licensed, see https://opensource.org/licenses/MIT
-   Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
