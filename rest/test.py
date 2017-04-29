#!/usr/bin/python3

from base import RestInterface

# 
# def paths(path):
#     if path is not None:
#         if isinstance(path, str):
#             yield path
#         else:
#             try:
#                 for item in path:
#                     yield item
#             except TypeError:
#                 yield path
# 
# pather = paths("bli")
# enumerate_ = enumerate(pather)
# print(next(enumerate_))
# # print(next(pather))
# 
# pather = paths(5)
# print(next(pather))
# 
# pather = paths((2, 4))
# print(next(pather))
# enumerate_ = enumerate(pather)
# print(next(enumerate_))
# print(next(pather))
# 
# pather = paths(None)
# try:
#     print(next(pather))
# except StopIteration:
#     print()







class Principal(object):
    
    def __init__(self, value=None):
        self.salad = value

print("pathify tests")
print("Test 1", list(RestInterface.pathify(None)))
print("Test 2", list(RestInterface.pathify(1)))
print("Test 3", list(RestInterface.pathify("jio")))
print("Test 4", list(RestInterface.pathify(("jio", 2))))
print()


print("get_point tests")

try:
    point, numeric, pointType = RestInterface.get_point(None, 0)
except TypeError as typeError:
    print(typeError)

try:
    point, numeric, pointType = RestInterface.get_point(None, 'key1')
except TypeError as typeError:
    print(typeError)

print("Test 1")
parent = []
point, numeric, pointType = RestInterface.get_point(parent, 0)
print(parent, point, numeric, pointType)
print()

print("Test 2")
parent = ['atfirst']
point, numeric, pointType = RestInterface.get_point(parent, 0)
print(parent, point, numeric, pointType)
print()

print("Test 3")
point, numeric, pointType = RestInterface.get_point(parent, 'key1')
print(parent, point, numeric, pointType)
print()

print("Test 4")
parent = {}
point, numeric, pointType = RestInterface.get_point(parent, 'key1')
print(parent, point, numeric, pointType)
print()

print("Test 5")
parent = {'key1': 8}
point, numeric, pointType = RestInterface.get_point(parent, 'key1')
print(parent, point, numeric, pointType)
print()

print("Test 6")
parent = Principal("one")
point, numeric, pointType = RestInterface.get_point(parent, 'salad')
print(parent, point, numeric, pointType)
print()

print("Test 7")
point, numeric, pointType = RestInterface.get_point(parent, 'nonsalad')
print(parent, point, numeric, pointType)
print()

print("get_path tests")

print("Test 1")
parent = None
path = None
value = RestInterface.get_path(parent, path)
print(parent, path, value)
print()

print("Test 2")
parent = "t1 parent"
path = None
value = RestInterface.get_path(parent, path)
print(parent, path, value)
print()

print("Test 3")
parent = None
path = 0
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("TypeError expected.")
except TypeError as error:
    print(parent, path, str(error))
print()

print("Test 4")
parent = []
path = 0
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("IndexError expected.")
except IndexError as error:
    print(parent, path, str(error))
print()

print("Test 5")
parent = {}
path = 0
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("TypeError expected.")
except TypeError as error:
    print(parent, path, str(error))
print()

print("Test 6")
parent = ["Blibb", "Abb"]
path = 2
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("IndexError expected.")
except IndexError as error:
    print(parent, path, str(error))
print()

print("Test 7")
parent = ["Blibb", "Abb"]
path = "keyZero"
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("KeyError expected.")
except KeyError as error:
    print(parent, path, str(error))
print()

print("Test 8")
parent = ["Blibb", "Abb"]
path = 0
value = RestInterface.get_path(parent, path)
print(parent, path, value)
path = 1
value = RestInterface.get_path(parent, path)
print(parent, path, value)
path = [1]
value = RestInterface.get_path(parent, path)
print(parent, path, value)
print()

print("Test 9")
parent = [0.0, [1.0, 1.1]]
path = 0
value = RestInterface.get_path(parent, path)
print(parent, path, value)
path = 1
value = RestInterface.get_path(parent, path)
print(parent, path, value)
path = [1]
value = RestInterface.get_path(parent, path)
print(parent, path, value)
path = (1, 0)
value = RestInterface.get_path(parent, path)
print(parent, path, value)
path = [0, 0]
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("TypeError expected.")
except TypeError as error:
    print(parent, path, str(error))
path = [0, 1]
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("TypeError expected.")
except TypeError as error:
    print(parent, path, str(error))
print()

parent = {'kaye': "valee", 'kdee': {'kb': "bee", 'ksee': "sea"}}
print("Test 10", parent)
path = None
value = RestInterface.get_path(parent, path)
print(path, value)
path = 'kaye'
value = RestInterface.get_path(parent, path)
print(path, value)
path = 3
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("TypeError expected.")
except TypeError as error:
    print(path, str(error))
path = ('kdee', 'kb')
value = RestInterface.get_path(parent, path)
print(path, value)
print()

parent = {
    'kaye': "valee"
    , 'kdee': {'kb': "bee", 'ksee': "sea"}
    , 'kale': [23, 45, 67]
    }
print("Test 11")
print(parent)
path = None
value = RestInterface.get_path(parent, path)
print(path, value)
path = 'kaye'
value = RestInterface.get_path(parent, path)
print(path, value)
path = 3
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("TypeError expected.")
except TypeError as error:
    print(path, str(error))
path = ('kale', 2)
value = RestInterface.get_path(parent, path)
print(path, value)
print()

parent = Principal("bobo")
print("Test 12")
print(id(parent), vars(parent))
path = None
value = RestInterface.get_path(parent, path)
print(path, id(value), value)
path = 0
try:
    value = RestInterface.get_path(parent, path)
    raise AssertionError("TypeError expected.")
except TypeError as error:
    print(path, str(error))
path = 'salad'
value = RestInterface.get_path(parent, path)
print(path, value)
path = ('salad', 1)
value = RestInterface.get_path(parent, path)
print(path, value)
print()

print("make_point tests")
restInterface = RestInterface()
print("Test", 1)
path = [0]
index = 0
point0 = None
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point0 = []
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point = ["ma"]
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
print()

print("Test", 2)
path = [1]
index = 0
point0 = None
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point0 = []
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point0 = ["ma"]
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point0 = ("ba",)
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point0 = {'car': "veh"}
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
print()

print("Test", 3)
path = ['memzero']
index = 0
point0 = None
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point0 = {}
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point0 = {'memzero': "Member Zero"}
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
point0 = ()
point1 = restInterface.make_point(path, index, point0)
print(path, index, point0, point1, point0 is point1)
print()

print("set_path tests")

restInterface = RestInterface()
test = "1"
print("Test", test)
path = [0]
value = "blob"
subTest = ".".join((test, "1"))
point0 = None
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "2"))
point0 = []
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "3"))
point0 = ["ma"]
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
print()

test = "2"
print("Test", test)
path = [1]
value = "blob"
subTest = ".".join((test, "1"))
point0 = None
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "2"))
point0 = []
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "3"))
point0 = ["ma"]
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "4"))
point0 = ("ba",)
print("Before", subTest, point0)
restInterface.verbose = True
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "5"))
point0 = {'car': "veh"}
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "6"))
point0 = {'tooky':0, 'wonkey': "babb"}
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "7"))
point0 = "Stringiness"
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
print()

test = "3"
print("Test", test)
subTest = ".".join((test, "1"))
point0 = ["Outer String"]
path = [0, 1]
value = "Inner"
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
subTest = ".".join((test, "2"))
point0 = [{'hand':"yy"}]
path = [0, 1]
value = "Inner"
print("Before", subTest, point0)
point1 = restInterface.set_path(point0, path, value)
print("After", subTest, path, value, point0, point1, point0 is point1)
print()



print("rest_put tests")
print("Test", 1)
restInterface = RestInterface()
restInterface.verbose = True
restInterface.rest_put(1)
# print(vars(restInterface))
print(restInterface.principal)
print()

print("Test", 2)
restInterface = RestInterface()
restInterface.rest_put(Principal("one"))
# print(vars(restInterface))
print(vars(restInterface.principal))
print()

print("Test", 3)
restInterface = RestInterface()
restInterface.verbose = True
restInterface.rest_put(Principal("two"), [0])
# print(vars(restInterface))
print(restInterface.rest_get())
print()

restInterface = RestInterface()
restInterface.rest_put(2, [0])
# print(vars(restInterface))
print(restInterface.rest_get())
print()

restInterface = RestInterface()
restInterface.verbose = True
restInterface.rest_put(2, [0,1])
print(restInterface.rest_get())
restInterface.rest_put(3, [0,2])
print(restInterface.rest_get())
restInterface.rest_put(4, [1])
# print(vars(restInterface))
print(restInterface.rest_get())
print()

restInterface = RestInterface()
# restInterface.verbose = True
restInterface.rest_put(['blib', 'blab'])
print(restInterface.rest_get())
restInterface.rest_put('bleb', (1,))
print(restInterface.rest_get())
print()

restInterface = RestInterface()
# restInterface.verbose = True
restInterface.rest_put({'keypie': 'cap'})
print(restInterface.rest_get())
restInterface.rest_put('bleb', ['keypie'])
print(restInterface.rest_get())
print()

restInterface = RestInterface()
# restInterface.verbose = True
restInterface.rest_put(Principal('bacon'))
print(vars(restInterface.rest_get()))
restInterface.rest_put('pork', ['salad'])
print(vars(restInterface.rest_get()))
print()

restInterface = RestInterface()
# restInterface.verbose = True
restInterface.rest_put('clap', ('piker',))
print(restInterface.rest_get())
restInterface.rest_put('bleb', ['keypit'])
print(restInterface.rest_get())
print()
