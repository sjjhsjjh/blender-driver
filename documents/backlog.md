Backlog
=======

-   Add a unit test like TestGameObject test_rest_list.

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
