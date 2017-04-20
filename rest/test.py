#!/usr/bin/python3

def enumerate_(dictOrList):
    try:
        list_ = dictOrList.keys()
    except AttributeError:
        list_ = range(len(dictOrList))
        
    for key in list_:
        print(key, dictOrList[key], isinstance(key, str), dictOrList.get(key))

enumerate_({'blib': 'blab', 'bleb': 10})

enumerate_(['ebbit', 'eloh', 15, 'gia'])
