#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Script to start Blender and Blender Driver.

This script starts Blender with command line parameters that causes it to
execute the Blender Driver launch script: blender_driver/launch.py

This could have been a shell or Perl script, but Blender itself is scripted in
Python. Making this also be Python reduces the number of technologies in
play. This script could be run by Python 2 or 3, depending on what the system
has. Supported versions of Blender all embed Python 3.

The script uses the __name__ == "main" idiom, so it can be imported and run
from another script like:

    # myblenderdriver.py

    import sys
    from blenderdriver import main
    
    main([sys.argv[0]]
         + ["--add", "switches", "-I", "always want here"]
         + sys.argv[1:])

See also the following.
-   https://blender.org
-   https://github.com/sjjhsjjh/blender-driver
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
#
# Module for pretty printing exceptions.
# https://docs.python.org/3/library/traceback.html#traceback-examples
from traceback import print_exc
#
# Local imports.
#
# Window and screen geometry utilities.
from windowgeometry import WindowGeometry

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
            description=textwrap.dedent(__doc__), epilog=
            "Switches for the Blender Driver launch script can be included."
            " Run blender_driver/launch.py --help.")
        #
        # Add all the command line switch definitions.
        self._argumentParser.add_argument(
            '-b', '--blend', help=
            "Path to a .blend file that Blender will open. Having a .blend file"
            " on the command line suppresses display of the splash.")
        self._argumentParser.add_argument(
            '-B', '--blender', help=
            "Path to the Blender executable. Default is to check a number of"
            " directories or rely on the PATH environment variable.")        
        self._argumentParser.add_argument(
            '-g', '--geometries', action='store_true', help=
            "Set the geometry of the Blender window, and the terminal window,"
            " if using. Geometries set are based on the size of the screen.")
        self._argumentParser.add_argument(
            '-l', '--launch', help=
            "Path to the launch script. Default is to assume it is the"
            " ../blender_driver/launch.py file, relative to the location of"
            " this script.")
        self._argumentParser.add_argument(
            '-r', '--record', help=
            "Record a screen capture video to the specified path,"
            " using recordmydesktop.")
        self._argumentParser.add_argument(
            '-t', '--terminal', action='store_true',
            help=
            "Open a new terminal window from which to run Blender. The Blender"
            " console output, including print output from the embedded Python,"
            " then appears in the terminal instead of wherever this script was"
            " run. Looks for a terminal program, either xterm or"
            " gnome-terminal, on the PATH environment variable.")
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
        if not self._arguments.geometries:
            return
        self._screenGeometry = WindowGeometry.from_X_display()
        self._terminalGeometry, self._blenderGeometry = self.get_geometries()
        if self._arguments.verbose:
            print('Screen geometry: {}'.format(vars(self._screenGeometry)))
            print('Blender geometry: {}'.format(vars(self._blenderGeometry)))

    def get_geometries(self):
        """Get sensible geometries for the terminal and blender.
        
        Terminal one is an X geometry in a single string. Blender one is a
        WindowGeometry object."""
        terminalGeometry = None
        screen = self._screenGeometry
        if screen.width < 1500:
            # Small screen.
            # Put the terminal in the lower left corner.
            # Put blender one sixth of the way across, the full height of the
            # screen and two thirds of the width.
            terminalGeometry = '80x48+0-0'
            blenderGeometry = WindowGeometry.from_xywh(
                screen.x + int(screen.width / 6), screen.y
                , int(screen.width * 2 / 3), screen.height)
            # blenderGeometry = (int(width / 6),     # X position.
            #                    0,                  # Y position.
            #                    int(width * 2 / 3), # Width.
            #                    height)             # Height.
        elif screen.width > 3000:
            # Big screen.
            # Make blender fill the upper right quadrant.
            # Put the terminal in the lower right quadrant.
            #
            # Y position gets a fudge factor to accomodate the border on the
            # Blender window, i.e. move the terminal down so it isn't under the
            # border.
            terminalGeometry = "80x48+{:0d}-0".format(int(screen.width/2))
            blenderGeometry = WindowGeometry.from_xywh(
                screen.x + int(screen.width/2), screen.y,
                int(screen.width/2), int(screen.height/2))
            # blenderGeometry = (int(width/2),   # X position.
            #                    int(height/2),  # Y position.
            #                    int(width/2),   # Width.
            #                    int(height/2) ) # Height.
            
        else:
            raise NotImplementedError(" ".join((
                "No specified geometry for screen dimensions:",
                vars(screen))))
        
        if self._arguments.record is not None:
            #
            # recordmydesktop requires multiples of 16 for all offsets and
            # sizes.
            blenderGeometry.round(16)

        return terminalGeometry, blenderGeometry    

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
    # the following.
    # import shutil
    # shutil.which()
    def which(self, program, extras=()):
        """Find a program on the operating system path after, optionally,
        checking in a list of extra directories."""
        for path in tuple(extras) + tuple(os.getenv("PATH", "").split(":")):
            candidate = os.path.join(path, program)
            if self._arguments.verbose:
                print('{} which({}) trying "{}"'.format(
                    self.argv0, program, candidate))
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
            command.extend(
                self._blenderGeometry.for_blender(self._screenGeometry))
        #
        # Add the .blend file, if specified.
        if self._arguments.blend is not None:
            command.append(self._arguments.blend)
        #
        # Append switches to make Blender launch Blender Driver, after loading
        # the .blend file. Also append a separator.
        launch = self._arguments.launch
        if launch is None:
            launch = os.path.abspath(os.path.join(
                os.path.dirname(__file__), os.pardir,
                "blender_driver", "launch.py"))
        command.extend(('--python', launch, '--'))
        #
        # Append verbosity switch, and any launcher arguments from the command
        # line.
        if self._arguments.verbose:
            command.append('--verbose')
        command.extend(self._launcherArguments)

        return command

    def get_blender(self):
        """Get the path of the Blender executable."""
        if self._arguments.blender is not None:
            return self._arguments.blender
        home = os.getenv('HOME', 'C:')
        directories = (
            os.path.join(home, 'blender-2.72b-OSX_10.6-x86_64', 'Blender',
                         'blender.app', 'Contents', 'MacOS' ),
            os.path.join(home, 'blender-2.79-linux-glibc219-x86_64')
        )
        blender = "blender"
        blenderPath = self.which(blender, directories)
        if blenderPath is None:
            if self._arguments.verbose:
                print(''.join((
                    "Couldn't find Blender executable \"", blender,
                    '" on path, nor in:\n\t"',
                    '"\n\t"'.join(directories),
                    '"\nWill rely on path environment.')))
            blenderPath = blender
        
        return blenderPath
    
    def _start_recorder(self, blenderPopen, blenderWindowName="Blender"):
        """\
        Start a screen recorder, if specified. Returns a Popen for the screen
        recorder process.
        """
        if self._arguments.record is None:
            return None
        
        if self._blenderGeometry is None:
            recorderGeometry = None
        else:
            #
            # Set the recorder geometry to be the same as the Blender window.
            # There's an issue that the Blender window mightn't have finished
            # initialising, which causes xwininfo to fail. So, keep trying until
            # one of the following applies:
            #
            # -   It works.
            # -   The Blender process seems to have ended.
            while True:
                try:
                    recorderGeometry = WindowGeometry.from_X_window(
                        blenderWindowName)
                    #
                    # If we get here then no exception was raised so we have a
                    # geometry and are ready to continue.
                    break
                
                except EnvironmentError as error:
                    #
                    # Assume no Blender window found. Check the process is still
                    # running.
                    blenderPopen.poll()
                    if blenderPopen.returncode is not None:
                        #
                        # No longer running. Fail by re-raising
                        raise
                    #
                    # Still running. Allow the code to go around the loop again.
                    if self._arguments.verbose:
                        print(error)
                        print("Trying again.")
        #
        # Assemble the recorder command line.
        recorderCommand = [
            'recordmydesktop', '--overwrite', '-o', self._arguments.record]
        if recorderGeometry is not None:
            recorderCommand.extend(recorderGeometry.for_recordmydesktop())
        #
        # Start the recorder.
        try:
            if self._arguments.verbose:
                print(" ".join((
                    self.argv0, 'Starting recorder:\n\t', '\n\t'.join((
                    '"'.join(("", _, "")) for _ in recorderCommand)))))
                recorder = subprocess.Popen(recorderCommand)
            else:
                #
                # Blender Python doesn't seem to have the subprocess.DEVNULL
                # constant.
                # TOTH: https://stackoverflow.com/a/8529412/7657675
                try:
                    devnull = subprocess.DEVNULL
                except AttributeError:
                    devnull = open(os.devnull, 'wb')
                #
                # Not verbose so discard all the recordmydesktop output. It
                # prints encoding progress to stdout, and messages to
                # stderr, so both get discarded.
                recorder = subprocess.Popen(
                    recorderCommand, stdout=devnull, stderr=devnull)
        except Exception as exception:
            print(''.join(("Failed to start recorder."
                           , ' Command line was:\n\t"'
                           , '"\n\t"'.join(recorderCommand)
                           , '"')))
            raise
        return recorder
    
    def _execute(self, command):
        """
        Start Blender, possibly in a terminal, and the screen recorder.
        """
        #
        # 
        return_ = 0
        try:
            popen = subprocess.Popen(command)
        except:
            print(''.join(('Failed to start Blender. Command line was:\n\t"'
                           , '"\n\t"'.join(command), '"')))
            print_exc()
            if self._arguments.blender is None:
                print("Try specifying an explicit path to the Blender"
                      " executable, with the -B switch.")
            return 1
        #
        # Start the screen recorder, if specified.
        try:
            recorder = self._start_recorder(popen)
        except:
            popen.terminate()
            print_exc()
            return 1
        #
        # Wait for Blender to finish, so that we can get a return code, and so
        # that we can stop the screen recorder.
        popen.wait()
        #
        # The next line gets 1 following a normal Blender quit from the user
        # interface. It's unfortunate but doesn't seem worth treating specially.
        return_ = popen.returncode
        #
        # Stop the screen recorder, if any.
        if recorder is not None:
            print("Stopping recorder and waiting for it to encode...")
            recorder.terminate()
            recorder.wait()
            print("Recorder finished OK." if recorder.returncode == 0 else
                  "Recorder failed: {}.".format(recorder.returncode))
        #
        # Return the Blender return code.
        return return_
    
    def main(self):
        """Run it."""
        #
        # Parse and store the command line options.
        self._parse_command_line()
        self._set_geometries()
        #
        # Create the command line. Start with the terminal command, or an empty
        # list.
        try:
            call = self._terminal_command()
        except EnvironmentError as error:
            # Could switch down to terminalCommand:None here instead.
            print(error)
            return 1
        #
        # Append the Blender command.
        try:
            call.extend(self._blender_command())
        except EnvironmentError as error:
            print(error)
            return 2
        #
        # And execute.
        return self._execute(call)

    def __init__(self, commandLine):
        """Constructor."""
        #
        # Set internal and static properties.
        self._terminalGeometry = None
        self._screenGeometry = None
        self._blenderGeometry = None
        self._set_argument_parser()
        #
        # Shallow copy the command line, for later, using a slice.
        self._commandLine = commandLine[:]

def main(commandLine):
    sys.exit(Main(commandLine).main())
    
if __name__ == '__main__':
    main(sys.argv)
