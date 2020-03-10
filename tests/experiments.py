"""
  * metaclass - This works! The mro looks to the metaclass for the variable on `class.variable = value` and calls
        __set__ on that object if exists.
  * decorator - Create a new class with the metaclass if needed.
"""

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

        class ClassPropertyMetaclass(my_type):
            def __new__(mcs, name, bases, attrs):
                for k, v in attrs.items():
                    if isinstance(v, class_property):
                        setattr(mcs, k, v)
                        print('found', k)
                return my_type.__new__(mcs, name, bases, attrs)

            is_class_property_meta = True
        return ClassPropertyMetaclass

    @classmethod
    def decorator(cls, new_cls=None):
        """Decorate a class to make it work with a class_property."""
        if new_cls is None:
            def wrapper(new_cls):
                return cls.decorator(new_cls)
            return wrapper

        if getattr(new_cls, 'is_class_property_meta', False):
            # Is already a metaclass
            return new_cls

        # What would I change here? Add variable type? This would add variable to all
        meta = cls.metaclass(new_cls)
        class NewClass(new_cls, metaclass=meta):
            pass

        # for k in dir(NewClass):
        #     v = getattr(NewClass, k, None)

        # Need to iterate through parent new_cls items for class_property
        for k, v in new_cls.__dict__.items():
            if isinstance(v, class_property):
                setattr(meta, k, v)
                print('found', k)

        # Return new class as metaclass
        return NewClass


def run():
    print('========== Metaclass ==========')
    class Meta(metaclass=class_property.metaclass()):
        v = class_property(1)

    Meta.v = 2  # Print set if successful
    Meta.v      # Print get if successful


    print('========== decorator ==========')
    @class_property.decorator
    class Descript(object):
        v = class_property(3)

    Descript.v = 4  # Print set if successful ...
    Descript.v      # Print get if successful


if __name__ == '__main__':
    run()
