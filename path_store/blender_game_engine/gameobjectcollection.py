#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for use with Blender Game Engine.

Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module that facilitates container subclasses.
# https://docs.python.org/3/library/collections.html#collections.UserList
import collections

class GameObjectList(collections.UserList):
    def __delitem__(self, specifier):
        list_ = self.data
        if isinstance(specifier, slice):
            for index in range(*specifier.indices(len(list_))):
                list_[index].endObject()
        else:
            list_[specifier].endObject()
    
        list.__delitem__(list_, specifier)

class GameObjectDict(collections.UserDict):
    def __delitem__(self, key):
        self.data[key].endObject()
        dict.__delitem__(self.data, key)
