import inspect
from functools import WRAPPER_ASSIGNMENTS


__all__ = ['metaclass', 'decorate', 'class_value', 'class_property']


def metaclass(inherit=object):
    """Create a custom metaclass to make the attribute use the `__set__` method.

    Normally `class.variable = value` would simply change the class value. By using a metaclass you can force
    `class.variable = value` to call the variable's `__set__` method.

    Args:
        inherit (object)[object]: Class object used in inheritance to avoid metaclass conflicts.

    Returns:
        metaclass (ClassPropertyMetaclass): Metaclass that looks for class_value attributes and registers them.
    """
    my_type = type(inherit)

    class ClassPropertyMetaclass(my_type):
        is_class_property_meta = True

        def __new__(mcs, name, bases, attrs):
            for k, v in attrs.items():
                mcs.register(k, v)
            return my_type.__new__(mcs, name, bases, attrs)

        @classmethod
        def register(cls, name, value):
            if isinstance(value, class_value):
                setattr(cls, name, value)

    return ClassPropertyMetaclass


def decorate(new_cls=None):
    """Decorate a class to make it work with a class_value or class_property.

    This class decorator will return a new class if the given class does not use a ClassPropertyMetaclass.

    Args:
        new_cls (object)[None]: Class to decorate

    Returns:
        new_cls (object): Given class or new class that will work with the class_value/class_property.
    """
    if new_cls is None:
        def wrapper(new_cls):
            return decorate(new_cls)
        return wrapper

    if getattr(new_cls, 'is_class_property_meta', False):
        return new_cls  # Is already a metaclass

    # Need to use a metaclass
    meta = metaclass(new_cls)

    class NewClass(new_cls, metaclass=meta):
        pass

    # Make the NewClass look like the given new_cls
    for attr in WRAPPER_ASSIGNMENTS:
        try:
            setattr(NewClass, attr, getattr(new_cls, attr))
        except (AttributeError, Exception):
            pass

    # Need to iterate through parent new_cls items to save the class_value/class_property
    for k, v in new_cls.__dict__.items():
        if isinstance(v, class_value):
            setattr(meta, k, v)

    # Return new class using a metaclass
    return NewClass


class class_value(object):
    """Class value that shares the same value with the class and any instance."""
    metaclass = staticmethod(metaclass)
    decorate = staticmethod(decorate)

    def __init__(self, value=None, doc=''):
        self.value = value
        self.__doc__ = doc

    def __get__(self, instance, owner=None):
        return self.value

    def __set__(self, obj, value):
        self.value = value


class class_property(class_value):
    """Property that works with the class and any instance."""
    def __init__(self, fget=None, fset=None, fdel=None, doc=''):
        super().__init__(None, doc)

        # Remove the value attribute
        del self.value

        # Set attributes
        self.fget = None
        self.fset = None
        self.fdel = None
        self.__doc__ = doc

        # Find num arguments
        self._fget_args = 0
        self._fset_args = 0
        self._fdel_args = 0

        # Call setting functions
        if fget is not None:
            self.getter(fget)
        if fset is not None:
            self.setter(fset)
        if fdel is not None:
            self.deleter(fdel)

    def __get__(self, instance, owner=None):
        if self.fget is None:
            raise AttributeError("unreadable attribute")

        if self._fget_args > 0:
            return self.fget(instance or owner)
        else:
            return self.fget()

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")

        if self._fset_args > 1:
            return self.fset(obj, value)
        else:
            return self.fset(value)

    def __delete__(self, instance=None):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")

        if self._fdel_args > 0:
            return self.fdel(instance)
        else:
            return self.fdel()

    def getter(self, fget):
        self.fget = fget

        if callable(self.fget):
            if not self.__doc__:
                self.__doc__ = self.fget.__doc__
            sig = inspect.signature(self.fget)
            self._fget_args = len(sig.parameters)
        else:
            self._fget_args = 0

        return self

    def setter(self, fset):
        self.fset = fset

        if callable(self.fset):
            sig = inspect.signature(self.fset)
            self._fset_args = len(sig.parameters)
        else:
            self._fset_args = 0

        return self

    def deleter(self, fdel):
        self.fdel = fdel

        if callable(self.fdel):
            sig = inspect.signature(self.fdel)
            self._fdel_args = len(sig.parameters)
        else:
            self._fdel_args = 0

        return self
