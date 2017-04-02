Blender Driver
==============
The Blender Driver project was originally about running a Python HTTP server
from within a Blender Game Engine (BGE) instance. The server could receive input
from a web browser, REST client, or other similar software. It would then use
the BGE Python interface to feed commands into a three-dimensional scene.

Under Construction
------------------
This repository is under construction. Code is being transferred here from an
unpublished proof-of-concept (POC). Current features are:

-   Spawn a thread when BGE starts and update the scene from the thread
    periodically.
    
Getting Started
===============
To get started with Blender Driver, you will need:

-   A copy of Blender, which is available from
    the [https://blender.org](https://blender.org) home page.
-   The code in this repository.

Confirm your installation is OK by running one of the demonstrations. There are
scripts to facilitate this. For example, run this:

    blender-driver/scripts/marker.py -B /path/to/your/Blender-install/blender

The demonstration should start. Press any key to stop the demonstration, then
key Escape to clear the Blender splash, then Ctrl-Q Return to quit Blender.

The demonstration should look like the video here:
[https://vimeo.com/210125332](https://vimeo.com/210125332)

Next Steps
==========
After confirming your installation is OK, try one of the other demonstrations in
the applications/ directory. Maybe take a copy of the scripts/marker.py file and
modify it.

The core Blender Driver code is in the blender_driver/ directory.

If you want to know why some things are how they are, then look in the
diagnostics/ directory, or run the diagnostic application, which is in the
applications/ directory.

Notes
=====
Code in this project follows some elements of the
[PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).

License
=======
This file is:  

-   (c) 2017 Jim Hawkins.
-   MIT licensed, see https://opensource.org/licenses/MIT
-   Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
