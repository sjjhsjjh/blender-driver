#!/usr/bin/python3

from base import RestInterface

def enumerate_(dictOrList):
    try:
        list_ = dictOrList.keys()
    except AttributeError:
        list_ = range(len(dictOrList))
        
    for key in list_:
        print(key, dictOrList[key], isinstance(key, str), dictOrList.get(key))

# enumerate_({'blib': 'blab', 'bleb': 10})
# 
# enumerate_(['ebbit', 'eloh', 15, 'gia'])

class Principal(object):
    
    def __init__(self, value=None):
        self.salad = value

restInterface = RestInterface()
restInterface.rest_put(1)
# print(vars(restInterface))
print(restInterface.principal)

restInterface = RestInterface()
restInterface.rest_put(Principal("one"))
# print(vars(restInterface))
print(vars(restInterface.principal))

restInterface = RestInterface()
restInterface.rest_put(Principal("two"), [0])
# print(vars(restInterface))
print(restInterface.rest_get())

restInterface = RestInterface()
restInterface.rest_put(2, [0])
# print(vars(restInterface))
print(restInterface.rest_get())

restInterface = RestInterface()
restInterface.rest_put(2, [0,1])
print(restInterface.rest_get())
restInterface.rest_put(3, [0,2])
print(restInterface.rest_get())
restInterface.rest_put(4, [1])
# print(vars(restInterface))
print(restInterface.rest_get())

restInterface = RestInterface()
# restInterface.verbose = True
restInterface.rest_put(['blib', 'blab'])
print(restInterface.rest_get())
restInterface.rest_put('bleb', (1,))
print(restInterface.rest_get())

restInterface = RestInterface()
# restInterface.verbose = True
restInterface.rest_put({'keypie': 'cap'})
print(restInterface.rest_get())
restInterface.rest_put('bleb', ['keypie'])
print(restInterface.rest_get())

restInterface = RestInterface()
# restInterface.verbose = True
restInterface.rest_put(Principal('bacon'))
print(vars(restInterface.rest_get()))
restInterface.rest_put('pork', ['salad'])
print(vars(restInterface.rest_get()))

restInterface = RestInterface()
# restInterface.verbose = True
restInterface.rest_put('clap', ('piker',))
print(restInterface.rest_get())
restInterface.rest_put('bleb', ['keypit'])
print(restInterface.rest_get())

