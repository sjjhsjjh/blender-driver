#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Script to start Blender and Blender Driver.

This script:

-   Finds the Blender executable in one of a number of locations.
-   Looks for a terminal program, currently supports xterm and gnome-terminal.
    If there is a terminal program, then it will be used to launch Blender so
    that the console output appears there. Otherwise Blender console output
    appears wherever this script was run.
-   Starts Blender with command line parameters that causes it to execute the
    Blender Driver launch script: launch_blender_driver.py
-   Sets the geometries of the terminal and Blender windows, based on the size
    of the screen.

This could have been a shell or Perl script, but Blender itself is scripted in
Python. Making this also be Python reduces the number of technologies in
play.

The script uses the __name__ == "main" idiom, so it could be run from another
script like:

    # myblenderdriver.py

    import sys
    from blenderdriver import main
    
    main([sys.argv[0]]
         + ["--add", "switches", "-I", "always want here"]
         + sys.argv[1:])

See also https://blender.org
"""

# Standard library imports, in alphabetic order.
#
# Module for command line switches.
# https://docs.python.org/3.5/library/argparse.html
import argparse
#
# Module for system functions, and file and directory paths.
# https://docs.python.org/3.5/library/os.html
# https://docs.python.org/3.5/library/os.path.html
import os
#
# Module for regular expressions.
# https://docs.python.org/3.5/library/re.html
import re
#
# Module for running an external program.
# Only used to run xdpyinfo, which returns the screen size, and read its output.
# https://docs.python.org/3.5/library/subprocess.html
import subprocess
#
# Module for returning a value from the whole script and for access to the
# command line.
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
        """argparse.ArgumentParser instance for the script."""
        return self._argumentParser
    
    @property
    def argv0(self):
        return self._commandLine[0]
    
    def _set_argument_parser(self):
        #
        # Initialise a command line parser with the documentation comment of
        # this script.
        self._argumentParser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(__doc__),
            epilog="Switches for the launcher can be included.")
        #
        # Add all the command line switch definitions.
        self._argumentParser.add_argument(
            '-b', '--blend',
            help=
            "Path to a .blend file that Blender will open. Having a .blend file"
            " on the command line suppresses display of the splash.")
        self._argumentParser.add_argument(
            '-g', '--geometries', action='store_true',
            help="Set geometries for the terminal and Blender windows")
        self._argumentParser.add_argument(
            '-t', '--terminal', action='store_true',
            help="Run in a new terminal window.")
        self._argumentParser.add_argument(
            '-v', '--verbose', action='store_true',
            help="Verbose output.")
        #
        # Append <launcher options> to the usage line. Strip trailing
        # whitespace, which includes a line break. Remove "usage: " from the
        # start because it gets printed again by the default --help option.
        usage = self._argumentParser.format_usage().rstrip()
        if usage.startswith("usage: "):
            usage = usage[len("usage: "):]
        self._argumentParser.usage = ' '.join((usage, "<launcher options>"))
    
    def _parse_command_line(self):
        """Parse command line switches into a couple of internal properties."""
        #
        # Run the parser. Unknown arguments are assumed to be for the launcher.
        self._arguments, self._launcherArguments \
        = self.argumentParser.parse_known_args(self._commandLine[1:])

    def _set_geometries(self):
        # Get the geometry specifiers. Terminal is a string, Blender is a list.
        if self._arguments.geometries:
            self._terminalGeometry \
            , self._blenderGeometry = self.get_geometries()

    def get_geometries(self):
        """Get sensible geometries for the terminal and blender.
        
        Terminal one is an X geometry in a single string. Blender one is a list
        of values suitable for appending to its command line."""
        width, height =  self.get_X_resolution()
        terminalGeometry = None
        blenderGeometry = None
        if width < 1500:
            # Small screen.
            # Put the terminal in the lower left corner.
            # Put blender one sixth of the way across, the full height of the
            # screen and two thirds of the width.
            terminalGeometry = '80x48+0-0'
            blenderGeometry = (str(int(width / 6)),     # X position.
                               '0',
                               str(int(width * 2 / 3)), # Width.
                               str(height) )
        elif width > 3000:
            # Big screen.
            # Make blender fill the upper right quadrant.
            # Put the terminal in the lower right quadrant.
            #
            # Y position gets a fudge factor to accomodate the border on the
            # Blender window, i.e. move the terminal down so it isn't under the
            # border.
            terminalGeometry = '+'.join((
                '80x48', str(int(width/2)), str(int(height/2) + 100)))
            blenderGeometry = (str(int(width/2)),   # X position.
                               str(int(height/2)),  # Y position.
                               str(int(width/2)),   # Width.
                               str(int(height/2)) ) # Height.
            
        else:
            raise NotImplementedError(''.join((
                "No specified geometry for resolution. ",
                str(width), 'x', str(height))))

        return terminalGeometry, blenderGeometry    

    def get_X_resolution(self):
        """Get the width and height of the screen in pixels, by calling an X
        Windows tool."""
        xdpyinfo = subprocess.Popen(['xdpyinfo'], stdout=subprocess.PIPE)
        reDimensions = re.compile('.*dimensions:\s*([0-9]+)x([0-9]+)')
        width = None
        height = None
        for line in xdpyinfo.stdout.readlines():
            match = reDimensions.match(line)
            if match:
                if width is not None:
                    # Don't know how to engineer this.
                    print ''.join((
                        'get_X_resolution() Using second setting on line "',
                        line, '"'))
                xy = match.group(1, 2)
                width = int(xy[0])
                height = int(xy[1])
        return width, height
    
    def _terminal_command(self):
        if not self._arguments.terminal:
            return []
        return list(self.get_terminal(self._terminalGeometry))
    
    def get_terminal(self, geometry=None):
        """Get a terminal emulator command line by checking the path for a list
        of known terminal programs.
        
        Command line will include switch settings suitable for the terminal.
        Switches will include setting the window geometry, if specified. The
        last switch will be the execute introduction, so that the caller can
        append a command line."""
        terminals = ('xterm', 'gnome-terminal')
        terminalPath = None
        terminalStyle = None
        for terminal in terminals:
            terminalPath = self.which(terminal)
            if terminalPath is not None:
                terminalStyle = terminal
                break
        if terminalPath is None:
            raise EnvironmentError(''.join((
                'No terminal emulator on path. Tried: "',
                '" "'.join(terminals),
                '".')))
        terminalCommand = [terminalPath]
        if terminalStyle == 'xterm':
            if geometry is not None:
                terminalCommand += ["-geometry", geometry]
            terminalCommand += ["-title", "Blender Console",
                                # Font size should be set here but the -fs
                                # switch doesn't seem to have any effect.
                                "-fg", "black", "-bg", "white",
                                "-e"]
        elif terminalStyle == 'gnome-terminal':
            if geometry is not None:
                terminalCommand += ["--geometry", geometry]
            terminalCommand += ["--hide-menubar",
                                # Next command line parameter doesn't seem to
                                # work.
                                "--title", "Blender Console",
                                "--execute"]
        else:
            raise NotImplementedError(
                'Terminal emulator "' + terminalStyle+ '"')
    
        return tuple(terminalCommand)
    
    # When everything catches up to python 3.3 then this could be changed to use
    # shutil.which()
    # import shutil
    def which(self, program, extras=()):
        """Find a program on the operating system path after, optionally,
        checking in a list of extra directories."""
        for path in tuple(extras) + tuple(os.getenv("PATH", "").split(":")):
            candidate = os.path.join(path, program)
            if self._arguments.verbose:
                print self.argv0 + " which(" + program + ') trying "' \
                      + candidate + '"'
            if os.path.isfile(candidate):
                return candidate
        return None

    def _blender_command(self):
        """Assemble a Blender command line, or raise EnvironmentError if Blender
        isn't found."""
        #
        # Start with the path of the Blender executable. This will raise the
        # error, if necessary.
        command = [self.get_blender()]
        #
        # Add the geometry switch and value, if specified.
        if self._blenderGeometry is not None:
            command.append('--window-geometry')
            command.extend(self._blenderGeometry)
        #
        # Add the .blend file, if specified.
        if self._arguments.blend is not None:
            command.append(self._arguments.blend)
        #
        # Append switches to make Blender launch Blender Driver, after loading
        # the .blend file.
        command.extend(('--python',
                        os.path.join(self._workingDirectory,
                                     "launch_blender_driver.py") ))
        #
        # Append argument separator, and any launcher arguments from the command
        # line.
        command.append('--')
        #
        # Append verbosity arguments.    
        if self._arguments.verbose:
            command.append('--verbose')
        command.extend(self._launcherArguments)

        return command

    def get_blender(self):
        """Get the path of the Blender executable."""
        home = os.getenv('HOME', 'C:')
        directories = (
            os.path.join(home, 'blender-2.72b-OSX_10.6-x86_64', 'Blender',
                         'blender.app', 'Contents', 'MacOS' ),
            # os.path.join(home_dir, 'blender-2.77a-linux-glibc211-x86_64'),
            os.path.join(home, 'blender-2.78a-linux-glibc211-x86_64')
        )
        blender = "blender"
        blenderPath = self.which(blender, directories)
        if blenderPath is None:
            raise EnvironmentError(''.join((
                'Could not find Blender executable "', blender,
                '" on path, nor in:\n\t"',
                '"\n\t"'.join(directories),
                '"\n')))
        return blenderPath
    
    def _execute(self, command):
        if self._arguments.verbose:
            print self.argv0 + ' about to os.execv.'
            for commandi in command:
                print "\t\"" + commandi + '"'
        os.execv(command[0], command)
        print self.argv0 + " after os.execv() somehow."
        return 1
    
    def main(self):
        """Run it."""
        #
        # Parse and store the command line options.
        self._parse_command_line()
        self._set_geometries()
        #
        # Change to the top directory. Other paths will be relative to it.
        # This could be done in the terminal emulator, except that xterm doesn't
        # support that.
        os.chdir(self._workingDirectory)
        #
        # Assemble the command line.
        #
        # Start with the terminal command, or an empty list.
        try:
            call = self._terminal_command()
        except EnvironmentError as error:
            # Could switch down to terminalCommand:None here instead.
            print error
            return 1
        #
        # Append the Blender command, which includes the -- separator.
        try:
            call.extend( self._blender_command() )
        except EnvironmentError as error:
            print error
            return 2
        
        return self._execute(call)

    def __init__(self, commandLine):
        """Constructor."""
        #
        # Set internal and static properties.
        self._terminalGeometry = None
        self._blenderGeometry = None
        self._set_argument_parser()
        #
        # Copy the command line, for later.
        self._commandLine = commandLine[:]
        #
        # Set the working directory based on the path of this script.
        self._workingDirectory = os.path.abspath(os.path.dirname(self.argv0))
        

def main(commandLine):
    sys.exit( Main(commandLine).main() )
    
if __name__ == '__main__':
    main(sys.argv)
