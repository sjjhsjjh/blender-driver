#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for window and screen geometry.

This file can only be used as a module."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for running an external program.
# Only used to run xdpyinfo, which returns the screen size, and read its output.
# https://docs.python.org/3.5/library/subprocess.html
import subprocess

class WindowGeometry(object):
    """
    Represents a screen window, i.e. an X Y offset, and a width and a height.
    """
    #
    # Co-ordinates of the top-left corner of the window, measured from the
    # top-left corner of the screen.
    x = None
    y = None
    #
    # Dimensions.
    width = None
    height = None
    
    _xwininfoMap = {
        "Absolute upper-left X": 'x',
        "Absolute upper-left Y": 'y',
        "Width": 'width',
        "Height": 'height'}
    
    @classmethod
    def from_X_display(cls, *args):
        """Construct and call set_from_X_display. Factory method."""
        return cls().set_from_X_display(*args)

    @classmethod
    def from_X_window(cls, *args):
        """Construct and call set_from_X_window. Factory method."""
        return cls().set_from_X_window(*args)
    
    def copy(self):
        return_ = self.__class__()
        return_.x = self.x
        return_.y = self.y
        return_.width = self.width
        return_.height = self.height
        return return_

    def set_from_X_display(self, ignoreWindowManager=False):
        """
        Set geometry to the size of the X display, by calling xwininfo.
        """
        self.set_from_xwininfo(('xwininfo','-root'))
        if ignoreWindowManager:
            return self

        # OK, pretty rudimentary handling of the window manager:
        # xfce4 only, and assumes there is a single panel.
        try:
            panel = self.__class__.from_X_window("xfce4-panel")
        except:
            panel = None
        
        if panel is None:
            return self
         
        if panel.width == self.width:
            # Horizontal panel.
            if panel.x == 0:
                self.y += panel.height
            self.height -= panel.height
        elif panel.height == self.height:
            # Vertical panel.
            if panel.y == 0:
                self.x += panel.width
            self.width -= panel.width
            
        return self
        
    def set_from_X_window(self, windowName):
        return self.set_from_xwininfo(('xwininfo','-name', windowName))

    def set_from_xwininfo(self, command):
        xwininfo = subprocess.Popen(command
                                    , universal_newlines=True
                                    , stdout=subprocess.PIPE
                                    , stderr=subprocess.PIPE)
        
        for line in xwininfo.stdout.readlines():
            key, colon, value = (_.strip() for _ in line.partition(":"))
            if colon != ":":
                continue
            try:
                setattr(self, self._xwininfoMap[key], int(value))
            except KeyError:
                pass
        error = ''.join(_ for _ in xwininfo.stderr.readlines())
        xwininfo.wait()
        if xwininfo.returncode != 0:
            raise EnvironmentError(
                'Failed to get X geometry: {:d}. Command: "{}". {}'.format(
                    xwininfo.returncode, '" "'.join(command), error))
        return self

    @classmethod
    def from_xywh(cls, *args):
        """
        Construct and call set_from_xywh. Factory method.
        """
        return cls().set_from_xywh(*args)
    
    def set_from_xywh(self, x, y=None, width=None, height=None):
        """
        Set the geometry from four values, or a sequence of four values.
        Returns self.
        """
        if y is None:
            # Assume x is subscriptable.
            self.x = x[0]
            self.y = x[1]
            self.width = x[2]
            self.height = x[3]
        else:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
        return self
    
    @staticmethod
    def _round_xy(value, base):
        return_ = int(value / base) * base
        if return_ < value:
            return_ += base
        return return_
    
    def round(self, base):
        self.x = self._round_xy(self.x, base)
        self.y = self._round_xy(self.y, base)
        self.width = int(self.width / base) * base
        self.height = int(self.height / base) * base
        return self
    
    def for_blender(self, screenGeometry=None):
        """
Sequence of values suitable for adding to a command line for Blender. The
Blender geometry origin is the bottom-left corner of the screen, so a
WindowGeometry object for the screen must also be supplied. If None is passed,
this subroutine gets the display size itself.
        """
        if screenGeometry is None:
            screenGeometry = self.__class__.from_X_display()
        return ('--window-geometry',) + tuple(str(int(_)) for _ in (
            self.x
            , (screenGeometry.y + screenGeometry.height) - self.y
            , self.width
            , self.height))
    
    def for_recordmydesktop(self):
        """
Sequence of values suitable for adding to a command line for the recordmydesktop
utility.
        """
        return (
            '-x', str(int(self.x))
            , '-y', str(int(self.y))
            , '--width', str(int(self.width))
            , '--height', str(int(self.height)))
    
