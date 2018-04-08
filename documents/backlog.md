Backlog
=======

-   Unit tests for animation in blender driver applications. Including:

    -   Get rid of the logging.

-   Boost phases to a property of the custom TestCase subclass.

-   Boost elapsed time between ticks to be in the custom TestCase subclass.

-   Add a unit test for Blender Python not having the subprocess.DEVNULL
    constant.

-   Uplift path store blender game engine into a sub-package.

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

-   Maybe change some implementations to inherit from UserDict or UserList.

    https://docs.python.org/3.5/library/collections.html#collections.UserDict

License
=======
This file is:  

-   (c) 2018 Jim Hawkins.
-   MIT licensed, see https://opensource.org/licenses/MIT
-   Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
