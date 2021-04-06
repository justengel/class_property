import inspect
import contextlib
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
            # Find all new class values
            class_values, attrs = mcs.split_class_values(attrs, bases)

            # Create the class object without the class values
            cls = super().__new__(mcs, name, bases, attrs)

            # Register or set the value for the new class_value
            mcs.register(cls, class_values)

            return cls

        @staticmethod
        def split_class_values(attrs, bases=None):
            """Split out the class values from the given dictionary of attributes."""
            if bases is None:
                bases = tuple()

            # Find all new class values
            class_values = {}
            for k, v in list(attrs.items()):
                # isinstance(getattr(meta, k, None), class_value):
                try:
                    if isinstance(v, class_value) or \
                            any((isinstance(base.__class__.__dict__.get(k, None), class_value) for base in bases)):
                        class_values[k] = v
                        attrs.pop(k, None)
                except (KeyError, AttributeError, Exception):
                    pass

            return class_values, attrs

        @classmethod
        def register(mcs, cls, class_values):
            """Register class_value object to this metaclass. Inherited classes that share the same metaclass will
            share the same class_value.

            Setting a class property needs to have the property exist in both the metaclass and the class. The best way
            to do this is to delete an existing property on the metaclass and class then set the new property on the
            class then metaclass.

            >>> cv = class_value(1)
            >>> delattr(metaclass, 'value')
            >>> delattr(MyClass, 'value')
            >>> setattr(MyClass, 'value', cv)
            >>> setattr(metaclass, 'value', cv)

            Args:
                cls (class/object/type): Class to save the class values with.
                class_values (dict): Dictionary of {attr_name: value} pairs.
            """
            # Register or set the value for the new class_value
            for k, v in class_values.items():
                # Check if class has this class value
                this_cv = mcs.__dict__.get(k, None)
                if not isinstance(this_cv, class_value):
                    # Set a new class value
                    if not isinstance(v, class_value):
                        v = class_value(v)

                    # Must set the class attribute, so instance objects have access
                    # Must set the metaclass attribute, so class objects have access
                    set_class_property(cls, k, v, metaclass=mcs)

                else:
                    # Just change the current value
                    if isinstance(v, class_value):
                        if type(v) != class_values:
                            # Change the class_value type (to class_property or something else)
                            for base in cls.__bases__[::-1]:
                                if isinstance(base, mcs) and k in base.__dict__:
                                    # Must set the class attribute, so instance objects have access
                                    # Must set the metaclass attribute, so class objects have access
                                    set_class_property(base, k, v, metaclass=mcs)
                                    break
                            else:  # If not break
                                # Must set the class attribute, so instance objects have access
                                # Must set the metaclass attribute, so class objects have access
                                set_class_property(cls, k, v, metaclass=mcs)
                            this_cv = v

                        # Get the new value
                        try:
                            v = v.__get__(cls, cls)
                        except (NameError, AttributeError, Exception):
                            continue  # Cannot get value due to name error. The class must be defined first.

                    # Set the class_value with the new value
                    try:
                        this_cv.__set__(cls, v)
                    except (NameError, AttributeError, Exception):
                        pass  # Cannot set value due to name error. The class must be defined first.

    ClassPropertyMetaclass.__name__ = '{}Metaclass'.format(inherit.__name__)
    return ClassPropertyMetaclass


@contextlib.contextmanager
def disable_property(obj, name):
    """Temporarily disable properties/attributes in the class bases with the given name
    so they can be set on the new class."""
    props = {}

    # Delete properties with the name so descriptors with __get__ and __set__ are not called when changing descriptors
    try:
        for base in obj.__bases__:
            if name in base.__dict__:
                props[base] = base.__dict__[name]
                delattr(base, name)
    except (AttributeError, Exception):
        pass

    # Run the with context block
    yield props

    # Reset the properties
    for base, v in props.items():
        setattr(base, name, v)


def set_class_property(cls, name, value, metaclass=None):
    """Set property helper method

    Setting a class property needs to have the property exist in both the metaclass and the class. The best way
    to do this is to delete an existing property on the metaclass and class then set the new property on the
    class then metaclass.

    >>> cv = class_value(1)
    >>> delattr(metaclass, 'value')  # Need to delete attr from metaclass.__bases__ first as well
    >>> delattr(MyClass, 'value')  # Need to delete attr from MyClass.__bases__ first as well
    >>> setattr(MyClass, 'value', cv)  # Can only setattr if no property/descriptor with __get__ and __set__ exists.
    >>> setattr(metaclass, 'value', cv)  # Can only setattr if no property/descriptor with __get__ and __set__ exists.

    Args:
        cls (type/object): Class object to set the class_value/class_property to.
        name (str): Name of the attribute (variable name).
        value (class_value): Class value/property to set to the class and metaclass
        metaclass (type/object): Class metaclass to set class_value/class_property to so class object has access.
    """
    with contextlib.suppress(AttributeError, Exception):
        delattr(metaclass, name)  # Delete the metaclass attribute, so the metaclass attribute can be set
    with contextlib.suppress(AttributeError, Exception):
        delattr(cls, name)  # Delete the class attribute, so the class attribute can be set (instead of calling __set__)

    with disable_property(metaclass, name):
        # Disable the metaclass first, so the class attribute can be set
        with disable_property(cls, name):
            setattr(cls, name, value)  # Set the class attribute, so instance objects have access

        # Set the metaclass attribute, so class objects have access
        if metaclass is not None:
            setattr(metaclass, name, value)


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

    # Create a new class using the metaclass
    NewClass = meta(new_cls.__name__, new_cls.__bases__, new_cls.__dict__.copy())

    # Make the NewClass look like the given new_cls
    for attr in WRAPPER_ASSIGNMENTS:
        try:
            setattr(NewClass, attr, getattr(new_cls, attr))
        except (AttributeError, Exception):
            pass

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
