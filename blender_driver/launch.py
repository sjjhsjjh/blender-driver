#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver launch script.

This script is intended to be run from the Blender command line, using the
--python switch.

This script:

-   Extends the Python module path so that the Blender Driver code can be
    imported.
-   Kicks everything off.

The command line to run this script is expected to be as follows.

    blender \\
        --blender_switches \\
        <blah>.blend \\
        --python /path/to/blender_driver/launch.py \\
        -- --switches-for launch_script \\
        -- --switches-for application

Specifying a .blend file is optional.

Tip: Use the blenderdriver.py script to create and run the command line.
"""

# Standard library imports, in alphabetic order.
#
# Module for command line switches.
# https://docs.python.org/3.5/library/argparse.html
import argparse
#
# Module for dynamic import.
# https://docs.python.org/3.5/library/importlib.html
import importlib
#
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Module for file and directory paths.
# https://docs.python.org/3.5/library/os.path.html
import os.path
#
# Module for extending the search path and for access to the command line.
# https://docs.python.org/3.5/library/sys.html
import sys
#
# Module for text dedentation.
# Only used for --help description.
# https://docs.python.org/3/library/textwrap.html
import textwrap

class Main(object):
    @property
    def argumentParser(self):
        """argparse.ArgumentParser instance for the Blender Driver launch
        script."""
        return self._argumentParser
    
    @property
    def argv0(self):
        return self._commandLine[self._scriptIndex]
    
    def _set_argument_parser(self):
        #
        # Initialise a command line parser with the documentation comment of
        # this script.
        self._argumentParser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(__doc__))
        #
        # Add all the command line switch definitions.
        self._argumentParser.add_argument(
            '--applicationClass', default="Application", help=
            'Class name of the driver application. Default is "Application".')
        self._argumentParser.add_argument(
            '--applicationModule',
            help=
            "Module that contains the driver application class."
            " Default if a <path>/<filename>.blend file was specified is the "
            " <path>/<filename>.py file, or blender_driver/application.py"
            " otherwise." )
        self._argumentParser.add_argument(
            '--controllersModule', default="controllers",
            help=
            "Diagnostic option."
            " Name of the module that contains the Blender Game Engine"
            ' controller subroutines. By default "controllers".' )
        self._argumentParser.add_argument(
            '--controllersPackage', 
            help=
            "Diagnostic option."
            " Name of the package that contains the Blender Game Engine"
            " controllers module. By default, the blender_driver package.")
        self._argumentParser.add_argument(
            '--gateway', default="driverGateway",
            help=
            "Name to give the driver gateway object."
            " By default: driverGateway.")
        self._argumentParser.add_argument(
            '-v', '--verbose', action='store_true', help='Verbose output.')
        self._argumentParser.add_argument(
            '-s', '--start', action='store_true',
            help=
            "Start the game engine. Selecting this option means that this"
            " script doesn't finish until the game engine exits.")
        self._argumentParser.usage = "See full help."
        
    def _parse_command_line(self):
        """Parse command line switches into an internal property."""
        #
        # The commandLine array includes the whole Blender command line, which
        # could have been assembled and invoked by the blenderdriver.py script.
        # Locate the parts that are used by this script.
        #
        # Locate the --python switch. The item after it will be the path of this
        # script. Set a convenience variable for that item.
        try:
            self._scriptIndex = self._commandLine.index("--python") + 1
        except ValueError:
            self._scriptIndex = 0
            self._argumentParser.prog = os.path.basename(self.argv0)
            raise
        #
        # Locate the .blend file. Its name and directory are assumed to be the
        # name and directory of the driver application's module too.
        self._blendIndex = None
        for index in range(len(self._commandLine)):
            if self._commandLine[index].endswith(".blend"):
                self._blendIndex = index
        #
        # Locate the -- separator between the Blender switches and the Python
        # switches, if there is one.
        commandLine = []
        try:
            optIndex = self._commandLine.index("--") + 1
        except ValueError:
            optIndex = None
        #
        # Locate the second -- separator, if there is one, which is between the
        # launch script options and the application options.
        applicationIndex = None
        try:
            if optIndex is not None:
                applicationIndex = self._commandLine.index(
                    "--", optIndex + 1) + 1
        except ValueError:
            pass
        #
        # Extract the command line.
        if optIndex is not None:
            if applicationIndex is None:
                commandLine[:] = self._commandLine[optIndex:]
            else:
                commandLine[:] = self._commandLine[optIndex:applicationIndex-1]       
        #
        # Run the parser.
        self._argumentParser.prog = os.path.basename(self.argv0)
        self._arguments = self._argumentParser.parse_args(commandLine)
        #
        # Set up logging.
        loggingModule = importlib.import_module("blender_driver.loggingutils")
        print(loggingModule.initialise_logging(self._arguments.verbose))
        #
        # Dump the command line.
        arguments = ["Command line:"]
        for index, argument in enumerate(self._commandLine):
            if index == self._scriptIndex:
                flag = '*'
            elif index == optIndex:
                flag = '+'
            elif index == self._blendIndex:
                flag = '-'
            elif index == applicationIndex:
                flag = '^'
            else:
                flag = ' '
            arguments.append('{}{:>2} {}'.format(
                flag, index, self._commandLine[index]))
        log(DEBUG, "\n".join(arguments))
        
        if applicationIndex is None:
            self._arguments.applicationSwitches = []
        else:
            self._arguments.applicationSwitches = self._commandLine[
                applicationIndex: ]
                
    def _module_from_blend(self):
        """Generate a module name from the path of the .blend file on the full
        command line. Assume it is in the same directory as the .blend file,
        and has the same name but with a .py extension, and the class is named
        Application."""
        scriptPath = os.path.abspath(self.argv0)
        blendPath = os.path.abspath(self._commandLine[self._blendIndex])
        #
        # The .blend file could be in a sub-directory, in which case the
        # corresponding .py file will also be in a sub-directory, which must be
        # a Python package.
        log(DEBUG, "{}".format({
            'scriptPath': scriptPath, 'blendPath': blendPath}))
        commonPath = os.path.commonpath((scriptPath, blendPath))
        #
        # ToDo: Something if there isn't a commonpath.
        #
        modulePath = blendPath[len(commonPath):]
        moduleName = os.path.splitext(os.path.basename( blendPath ))[0]
        modulePath = os.path.dirname(modulePath)
        #
        # Create a Python module name, with dot separators, from the path of the
        # .blend file, which will have directory separators.
        while True:
            #
            # Remove the last directory from the path.
            modulePath, directory = os.path.split(modulePath)
            if directory == '':
                break
            #
            # Add it to the module name.
            moduleName = '.'.join((directory, moduleName))
        log(DEBUG, "{}".format({
            'commonPath': commonPath, 'modulePath': modulePath
            , 'moduleName': moduleName}))
        return moduleName
    
    def _import_application_module(self):
        #
        # Get the full name of the module that includes the application's driver 
        # subclasses.
        if self._arguments.applicationModule is not None:
            # Explicit package and module on command line.
            moduleName = self._arguments.applicationModule
        elif self._blendIndex is not None:
            # Derive it from the path of the .blend file.
            moduleName = self._module_from_blend()
        else:
            # Not specified, use the blender_drive base module.
            # It contains the classes of which a driver application's classes
            # would be subclasses.
            moduleName = "blender_driver.application.base"

        # ToDo: This assumes that the application module is in a sub-directory
        # that is already on sys.path and therefore can be imported. Fix that.

        log(DEBUG, 'Importing application module "{}"'.format(moduleName))
        self._applicationModule = importlib.import_module(moduleName)

    def _prepare_import(self):
        """Prepare to import modules, by adding the directory in which this
        script is located to the places from where modules can be loaded. This
        makes it possible to import the modules in the blender_driver package.
        
        Returns a message that can be logged.
        
        Doesn't print the message itself because the logging set-up module can
        only be loaded after preparation, and logging levels can only be set
        after parsing the command line.
        """
        parentDir = os.path.join(os.path.dirname(__file__), os.path.pardir)
        sys.path.append(os.path.abspath(parentDir))
        
        return 'Added to module path "{}"'.format(sys.path[-1])
    
    def _import_modules(self):
        """Import the blender_driver module, and the application's driver
        module. Set a reference to the application module in an internal
        property.
        """
        #
        # Import module for bpy utility functions, dynamically.
        self._bpyutils = importlib.import_module("blender_driver.bpyutils")
        #
        # Also import the module for the driver application.
        self._import_application_module()

    def main(self):
        """Run it."""
        #
        # The local logging utilities have to be imported dynamically, which can
        # only be done after setting up the import path.
        importMessage = self._prepare_import()
        #
        # Parse and store the command line options.
        try:
            self._parse_command_line()
            log(DEBUG, importMessage)
        except ValueError as error:
            #
            # This point is reached if there wasn't a --python switch on the
            # command line. Assume that this is because it wasn't run from
            # Blender and so print the usage and exit with an error code 2.
            # 2 seems to be the exit code set by ArgumentParser if there is an
            # unrecognised switch.
            self._argumentParser.print_help()
            print(error)
            raise SystemExit(2)
        #
        # Sort out the modules.
        self._import_modules()
        # print(dir(self._applicationModule),
        #       self._applicationModule.__name__,
        #       self._applicationModule.__package__)
        #
        # Get a class object for the application and pass it to the next stage.
        applicationClass = getattr(self._applicationModule,
                                   self._arguments.applicationClass)
        self._bpyutils.load_driver(applicationClass, self._arguments )
        log(DEBUG, "Blender Driver launch script finished.")
        
    def __init__(self, commandLine):
        """Constructor."""
        #
        # Set internal and static properties.
        self._applicationModule = None
        self._scriptIndex = 0
        self._blendIndex = None
        self._set_argument_parser()
        #
        # Copy the command line, for later.
        self._commandLine = commandLine[:]

def main(commandLine):
    #
    # Don't necessarily call sys.exit here, because this script is intended to
    # be run from within Blender.
    Main(commandLine).main()
    
if __name__ == '__main__':
    #
    # The name is main if launched by Blender --python, or if launched from the
    # command line.
    main(sys.argv)
else:
    print('"'.join((
        'Blender Driver launch script name was ', __name__, '. Quitting.')))
