#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for hosted attributes.


Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order, would go here.
#
# Local imports, would go here.

class HostedProperty(property):
    """Custom Property subclass to represent values that are properties within
    an object in another property.
    """
    
    # Instances of this class get added to the class object, and the initialiser
    # is run in context of the class, not the instance. There needs to be some
    # way to initialise the property's host name and attribute name. This is a
    # kludge at the moment: Setting the property to None actually create a new
    # holder object and sets the host name and attribute name into it.

    class _Holder(object):
        """Inner class that gets set into the property in the principal class,
        not the host. It catches attempts to set items in immutable objects and
        replaces them by creating a new modifiable instance of the object,
        modifying it, then casting it back to the immutable type and setting it.
        """
        
        # The specifier parameter could, in all cases, be a slice or a simple
        # index.
        
        def _get_host_attr(self):
            host = getattr(self._instance, self._hostName)
            return host, getattr(host, self._attrName)
        
        def __getitem__(self, specifier):
            host, attr = self._get_host_attr()
            # print('_Holder getitem', {'specifier':specifier, 'attr':attr})
            return attr[specifier]

        def __setitem__(self, specifier, value):
            host, attr = self._get_host_attr()
            # print('_Holder setitem'
            #       , {'specifier':specifier, 'value':value, 'attr':attr})
            mutable = list(attr)
            mutable.__setitem__(specifier, value)
            # ToDo: Optimisation goes here.
            setattr(host, self._attrName, attr.__class__(mutable))
        
        def __delitem__(self, specifier):
            host, attr = self._get_host_attr()
            # print('_Holder delitem', {'specifier':specifier, 'attr':attr})
            mutable = list(attr)
            mutable.__delitem__(specifier)
            # ToDo: Optimisation goes here.
            setattr(host, self._attrName, attr.__class__(mutable))
        
        def __init__(self, instance, hostName, attrName):
            self._instance = instance
            self._hostName = hostName
            self._attrName = attrName

    def get(self, instance):
        return getattr(instance, self._propertyName)

    def set(self, instance, value):
        #
        # Setting to None initialises the holder.
        if value is None:
            setattr(instance
                    , self._propertyName
                    , self._Holder(instance, self._hostName, self._attrName))
        else:
            host = getattr(instance, self._hostName)
            attr = getattr(host, self._attrName)
            # Near here, we could have code like:
            #
            #     if attr is value:
            #         return
            #
            # It doesn't seem like a good idea though. It seems better to let
            # the host optimise its setter like that, if it wants to.
            if attr.__class__ is not value.__class__:
                value = attr.__class__(value)
            setattr(host, self._attrName, value)

    def delete(self, instance):
        delattr(instance, self._propertyName)
    
    def __init__(self, attrName, hostName, propertyName=None):
        """Default propertyName is "_" + attrName."""
        self._attrName = attrName
        self._propertyName = \
            ''.join(('_', attrName)) if propertyName is None else propertyName
        self._hostName = hostName
        super().__init__(self.get, self.set, self.delete)
