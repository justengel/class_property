"""
Tried to dynamically change the metaclass in order to set the class_property.

Did not find any success. It seems the best way is to just use a metaclass.

Resources:
    * https://www.python.org/dev/peps/pep-0487/
    * https://docs.python.org/3/reference/datamodel.html
    * https://docs.python.org/3/howto/descriptor.html
"""

# Cannot overwrite type methods
# type_set = type.__getattribute__
# def mytype_setattr(name, value=None):
#     print('here', name, value)
# type.__getattribute__ = mytype_setattr


def register_class_property(mcs, name, prop):
    """Register a class property to a metaclass, so `class.variable = value` calls the __set__ method."""
    if isinstance(prop, class_property):
        setattr(mcs, name, prop)


class class_property(object):
    def __init__(self, value=None, doc=''):
        self.value = value
        self.__doc__ = doc

    def __get__(self, instance, owner=None):
        print('<<<<< get <<<<<', self.value)
        return self.value

    def __set__(self, obj, value):
        print('>>>>> set >>>>>', value)
        self.value = value

    @classmethod
    def metaclass(cls, inherit=object):
        """Create an return a class_property metaclass to make the class use the __set__ function."""
        my_type = type(inherit)

        class SubClassPropertyMetaclass(my_type):
            def __new__(mcs, name, bases, attrs):
                for k, v in attrs.items():
                    register_class_property(mcs, k, v)
                return my_type.__new__(mcs, name, bases, attrs)

            is_class_property_meta = True

        return SubClassPropertyMetaclass

    def __set_name__(self, owner, name):
        print('----- set_name -----', owner, name)
        if getattr(owner, 'is_class_property_meta', False):
            print('successful metaclass')
            return  # Metaclass will register this object

        # Try to make override a metaclass?
        meta = type(owner)
        if meta == type:
            # Nothing seems to work
            print('metaclass is type')

            owner.__metaclass__ = meta = self.metaclass()  # No effect

            # TypeError: __class__ assignment only supported for heap types or ModuleType subclasses
            # owner.__class__ = self.metaclass()

        # Attach a base class with the metaclass to handle class properties
        # meta = self.metaclass(owner)
        # class MyBaseClassProperty(metaclass=meta):
        #     pass

        # Cannot set __mro__ (readonly attribute). mro() method doesn't seem to work either
        # owner.__mro__ = owner.__mro__ + (meta,)

        # Base class doesn't want to work either
        # owner.__bases__ = owner.__bases__ + (MyBaseClassProperty,)

        # Set the metaclass variable to this object to work for `class.variable = value`
        register_class_property(meta, name, self)


def run():
    print('========== __set_name__ ==========')
    class A(object):
        a = class_property(1)
        a2 = a

    A.a = 2  # Print set if successful
    A.a      # Print get if successful

    print('========== __set_name__ metaclass ==========')
    class B(metaclass=class_property.metaclass()):
        b = class_property(2)

    B.b = 2  # Print set if successful
    B.b      # Print get if successful


if __name__ == '__main__':
    run()
