#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store unit tests."""

# Standard library imports, in alphabetic order.
#
# Unit test module.
# https://docs.python.org/3.5/library/unittest.html
import unittest
#
# Local imports.
#
# Unit test tests.
from test.principal import TestPrincipal
#
# Unit test modules.
from test.strquote import TestStrQuote
from test.pathify import TestPathify
from test.descendone import TestDescendOne
from test.descend import TestDescend
from test.makepoint import TestMakePoint
from test.insert import TestInsert
from test.merge import TestMerge
from test.restput import TestRestPut
# Above should be done with .discover() but I couldn't get it to work.

# restInterface.rest_put(Principal("two"), [0])
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "4"))
# restInterface = RestInterface()
# restInterface.rest_put(2, [0])
# print(subTest, restInterface.rest_get())
# print()
# 
# test = "2"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put(2, [0,1])
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "2"))
# restInterface.rest_put(3, [0,2])
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "3"))
# restInterface.rest_put(4, [1])
# print(subTest, restInterface.rest_get())
# print()
# 
# test = "3"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put(['blib', 'blab'])
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "2"))
# restInterface.rest_put('bleb', (1,))
# print(subTest, restInterface.rest_get())
# print()
# 
# test = "4"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put({'keypie': 'cap'})
# print(subTest, restInterface.rest_get())
# restInterface.rest_put('bleb', 'keypie')
# print(subTest, restInterface.rest_get())
# print()
# 
# test = "5"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put(Principal('bacon'))
# print(subTest, vars(restInterface.rest_get()))
# subTest = ".".join((test, "2"))
# restInterface.rest_put('pork', ['salad'])
# print(subTest, vars(restInterface.rest_get()))
# print()
# 
# test = "6"
# print("Test", test)
# subTest = ".".join((test, "1"))
# restInterface = RestInterface()
# restInterface.rest_put('clap', ('piker',))
# print(subTest, restInterface.rest_get())
# subTest = ".".join((test, "2"))
# restInterface.rest_put('bleb', ['keypit'])
# print(subTest, restInterface.rest_get())
# print()

# To Do:
# -   Test with principal that has setters, and do the optimise ToDo in
#     pathstore.py file.

if __name__ == '__main__':
    unittest.main()