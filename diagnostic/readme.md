Blender Driver Diagnostic Modules
=================================
This directory contains code for diagnostic and demonstration versions of some
of the lower level parts of Blender Driver. If you want to run Blender Driver,
ignore this directory. If you want to understand how it works, read and run some
of this code.

Persistence in the Blender Game Engine Python instance
======================================================
Some of the diagnostic controller modules demonstrate different approaches to
persistence in the Blender Game Engine (BGE) Python instance. Some of the
approaches don't work. The best approach is used in the proper Blender Driver
controllers module.

The controller modules here don't run a Blender Driver application. Instead,
they load a module based on the classes in the driverutils module.
