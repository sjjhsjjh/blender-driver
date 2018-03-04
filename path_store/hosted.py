#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Path Store module for hosted attributes.


Cannot be run as a program, sorry."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for enum type.
# https://docs.python.org/3.5/library/enum.html
from enum import Enum
#
# Local imports, would go here.

class HostedProperty(property):
    """Custom Property subclass to represent values that are properties within
    an object in another property.
    """
    
    # Instances of this class get added to the class object, and the initialiser
    # is run in context of the class, not the instance. There needs to be some
    # way to initialise the property's host name and attribute name. This is a
    # kludge at the moment: Setting the property to None actually creates a new
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
        
        # This seemed like an interesting idea but __getattribute__ isn't
        # invoked for __ attributes, like __len__ for example.
        #
        # def __getattribute__(self, name):
        #     if name in (
        #         '_get_host_attr', '_instance', '_hostName', '_attrName'
        #         ):
        #         return object.__getattribute__(self, name)
        #     host, attr = self._get_host_attr()
        #     print('_Holder getattrbute', {'name':name, 'attr':attr})
        #     return attr.__getattribute__(name)
        #
        # It would be interesting to see if this class should somehow be a
        # subclass of attr.__class__.
        #
        # For now, __getattr__ has been implemented. That gives access to the
        # methods of the hosted property. It might also be a good idea to
        # implement the rest of that family in the same way:
        # - __setattr__
        # - __delattr__
        # - __dir__
        # See https://docs.python.org/3.5/reference/datamodel.html#object.__getattr__
        
        def __getattr__(self, name):
            host, attr = self._get_host_attr()
            # print('_Holder getattr', {'name':name, 'attr':attr})
            return getattr(attr, name)

        def __len__(self):
            host, attr = self._get_host_attr()
            return len(attr)
        
        def __getitem__(self, specifier):
            host, attr = self._get_host_attr()
            # print('_Holder getitem', {'specifier':specifier, 'attr':attr})
            return attr[specifier]

        def __setitem__(self, specifier, value):
            host, attr = self._get_host_attr()
            # print('_Holder setitem'
            #       , {'specifier':specifier, 'value':value, 'attr':attr})
            
            if hasattr(attr, '__setitem__'):
                try:
                    attr.__setitem__(specifier, value)
                    return
                except AttributeError:
                    pass

            mutable = list(attr)
            mutable.__setitem__(specifier, value)
            setattr(host, self._attrName, attr.__class__(mutable))
        
        def __delitem__(self, specifier):
            host, attr = self._get_host_attr()
            # print('_Holder delitem', {'specifier':specifier, 'attr':attr})
            if hasattr(attr, '__delitem__'):
                try:
                    attr.__delitem__(specifier)
                    return
                except TypeError:
                    pass

            mutable = list(attr)
            mutable.__delitem__(specifier)
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

class InterceptCast(Enum):
    """Enumeration for types of casting in the intercept set."""
    
    NONE=1
    """Never cast in the intercept set."""

    IFDIFFERENTNOW=2
    """Check the class of the destination property before every set."""
    
    IFDIFFERENTTHEN=3
    """Check the class of the destination property first time it is set, then
    assume it stays the same."""

class InterceptProperty(property):
    """Custom property subclass that intercepts access to a destination to:
    
    -   Cast values being set to the type of the destination.
    -   Make the destination mutable at the item level.
    
    This subclass is used in the Blender Driver project to make Blender Game
    Enginer (BGE) Vector properties mutable.
    """
    
    class _PropertyInstance(object):
        """Inner class of which an instance is set in order to implement
        interception in the instance.
        """
        
        # The following seemed like an interesting idea but __getattribute__
        # isn't invoked for __ attributes, like __len__ for example.
        #
        # def __getattribute__(self, name):
        #     if name in (
        #         '_get_host_attr', '_instance', '_hostName', '_attrName'
        #         ):
        #         return object.__getattribute__(self, name)
        #     host, attr = self._get_host_attr()
        #     print('_Holder getattrbute', {'name':name, 'attr':attr})
        #     return attr.__getattribute__(name)
        #
        # It would be interesting to see if this class should somehow be a
        # subclass of attr.__class__.
        #
        # For now, __getattr__, __setattr__, and __len__ have been implemented.
        # That gives access to the methods of the destination property. It might
        # also be a good idea to implement the rest of that family in the same
        # way:
        # - __delattr__
        # - __dir__
        # See https://docs.python.org/3.5/reference/datamodel.html#object.__getattr__

        def __getattr__(self, name):
            return getattr(self._destination_getter(self._instance), name)
        def __setattr__(self, name, value):
            attr = self._destination_getter(self._instance)
            attr.__setattr__(name, value)
            
        def __len__(self):
            return self._destination_getter(self._instance).__len__()

        def __getitem__(self, specifier):
            return self._destination_getter(self._instance)[specifier]

        def __setitem__(self, specifier, value):
            attr = self._destination_getter(self._instance)
            try:
                attr.__setitem__(specifier, value)
                return
            except AttributeError:
                # The Vector type in Blender Game Engine raises this error.
                pass
            
            # If the code gets here then it wasn't possible to setitem in the
            # destination. Handle it here instead.

            mutable = list(attr)
            mutable.__setitem__(specifier, value)
            if attr.__class__ is str:
                mutable = ''.join(str(_) for _ in mutable)
            self._intercept_setter(self._instance, mutable)
        
        def __delitem__(self, specifier):
            attr = self._destination_getter(self._instance)
            try:
                attr.__delitem__(specifier)
                return
            except AttributeError:
                pass
            except TypeError:
                # The Vector type in Blender Game Engine raises this error.
                pass

            mutable = list(attr)
            mutable.__delitem__(specifier)
            if attr.__class__ is str:
                mutable = ''.join(str(_) for _ in mutable)
            self._intercept_setter(self._instance, mutable)

        # ToDo: Decide whether to have bypass always, never, or sometimes.
        # def bypass(self):
        #     return self._destination_getter(self._instance)

        def __init__(self, instance, destination_getter, intercept_setter):
            # Have to make explicit use of the base class attribute setter,
            # because this class has its own __setattr__ method.
            object.__setattr__(self, '_instance', instance)
            object.__setattr__(self, '_destination_getter', destination_getter)
            object.__setattr__(self, '_intercept_setter', intercept_setter)
    
    def get(self, instance):
        try:
            attr = self._intercept_getter(instance)
        except AttributeError:
            attr = self._create_property_instance(instance)
        return attr
    
    def _create_property_instance(self, instance):
        attr = self._PropertyInstance(
            instance, self._destination_getter, self.set)
        self._intercept_setter(instance, attr)
        return attr

    def set(self, instance, value):
        # Near here, we could have code like:
        #
        #     if attr is value:
        #         return
        #
        # It doesn't seem like a good idea though. It seems better to let the
        # destination optimise its setter like that, if it wants to.

        if self._cast is not InterceptCast.NONE:
            if (
                self._cast is InterceptCast.IFDIFFERENTNOW
                or self._destinationPropertyClass is None
               ):
                self._destinationPropertyClass = \
                    self._destination_getter(instance).__class__
    
            if self._destinationPropertyClass is not value.__class__:
                value = self._destinationPropertyClass(value)

        self._destination_setter(instance, value)

    def delete(self, instance):
        self._intercept_deleter(instance)
        # ToDo: Maybe delete the destination too?
        
    def destination_setter(self, destination_setter):
        self._destination_setter = destination_setter
        return self
    def intercept_getter(self, intercept_getter):
        self._intercept_getter = intercept_getter
        return self
    def intercept_setter(self, intercept_setter):
        self._intercept_setter = intercept_setter
        return self
    def intercept_deleter(self, intercept_deleter):
        self._intercept_deleter = intercept_deleter
        return self
    
    def __call__(self, destination_getter):
        """This will be called as a decorator."""
        self._destination_getter = destination_getter
        return self
        
    def __init__(self, cast=InterceptCast.NONE):
        """Call to instantiate the property. The constructor isn't the
        decorator.
        """
        self._destinationPropertyClass = None
        self._cast = cast
        super().__init__(self.get, self.set, self.delete)

