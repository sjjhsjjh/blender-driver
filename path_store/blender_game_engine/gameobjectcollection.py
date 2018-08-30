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
# Data model reference documentation is also useful:
# https://docs.python.org/3/reference/datamodel.html#emulating-container-types

class GameObjectList(collections.UserList):
    def __delitem__(self, specifier):
        list_ = self.data
        if isinstance(specifier, slice):
            for index in range(*specifier.indices(len(list_))):
                if list_[index] is not None:
                    list_[index].endObject()
        else:
            if list_[specifier] is not None:
                list_[specifier].endObject()
    
        list.__delitem__(list_, specifier)
    
    def __setitem__(self, index, value):
        item = self.data[index]
        if item is not value and item is not None:
            item.endObject()
        list.__setitem__(self.data, index, value)

class GameObjectDict(collections.UserDict):
    def __delitem__(self, key):
        object_ = self.data[key]
        if object_ is not None:
            object_.endObject()
        dict.__delitem__(self.data, key)
    
    def __setitem__(self, key, value):
        item = self.data[key]
        if item is not value and item is not None:
            item.endObject()
        dict.__setitem__(self.data, key, value)
