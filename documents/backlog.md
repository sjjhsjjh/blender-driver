Backlog
=======

-   Unit tests for animation in blender driver applications. Including:

    -   Animation works.
    -   Animation objects get set to None in the path store.
    -   Physics gets suspended and resumed.
    -   Get rid of the logging.

-   See about moving prepare animation and suspend restore into the core
    application classes. Maybe a physics.py server on top of rest.py
    
    Replace the userData number matching with a reference to the object, in
    rest.py PathAnimation class. It could be set by the startTime setter.
    
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

-   Fix problem that recording only works with --verbose.
