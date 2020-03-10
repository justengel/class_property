
def test_class_value_usage():
    from class_property import class_value

    # doesn't matter if class_value.decorate, class_property.decorate, or decorate (same with metaclass)
    class MyClass(object, metaclass=class_value.metaclass()):
        value = class_value(1)

    mc = MyClass()
    assert mc.value == 1
    assert MyClass.value == 1

    MyClass.value = 3
    assert mc.value == 3
    assert MyClass.value == 3

    mc.value = 2
    assert mc.value == 2
    assert MyClass.value == 2


    class SubClass(MyClass):
        hello = class_value("World")

    sub = SubClass()
    SubClass.hello = 'name'
    assert sub.hello == 'name'
    assert SubClass.hello == 'name'

    sub.hello = 'John Doe'
    assert sub.hello == 'John Doe'
    assert SubClass.hello == 'John Doe'

    sub.value = 7
    assert SubClass.value == 7
    assert sub.value == 7
    assert mc.value == 7
    assert MyClass.value == 7


def test_class_property_usage():
    from class_property import class_value, class_property, decorate, metaclass

    global GLOB
    GLOB = 'Hello'

    def get_glob():
        """Return the global GLOB value"""
        global GLOB
        return GLOB

    def set_glob(value):
        global GLOB
        GLOB = value

    # doesn't matter if class_value.decorate, class_property.decorate, or decorate (same with metaclass)
    @decorate
    class MyClass(object):
        _VALUE = None

        @class_property
        def value(self):
            return MyClass._VALUE

        @value.setter
        def value(self, value):
            MyClass._VALUE = value

        # Also works with no arguments
        @class_property
        def value2():
            return MyClass._VALUE

        @value2.setter
        def value2(value):
            MyClass._VALUE = value

        glob = class_property(get_glob, set_glob)

    mc = MyClass()
    assert mc.value is None
    assert MyClass.value is None
    MyClass.value = 3
    assert mc.value == 3
    assert MyClass.value == 3
    mc.value = 2
    assert mc.value == 2
    assert MyClass.value == 2

    assert mc.value2 == 2
    assert MyClass.value2 == 2
    mc.value2 = 5
    assert mc.value == 5
    assert MyClass.value == 5
    assert mc.value2 == 5
    assert MyClass.value2 == 5

    assert MyClass.glob == 'Hello'
    assert mc.glob == 'Hello'
    MyClass.glob = 'Jack'
    assert MyClass.glob == 'Jack'
    assert mc.glob == 'Jack'
    mc.glob = 'Jill'
    assert MyClass.glob == 'Jill'
    assert mc.glob == 'Jill'


    class SubClass(MyClass):
        pass

    sub = SubClass()
    sub.glob = 'John'
    assert SubClass.glob == 'John'
    assert sub.glob == 'John'
    assert MyClass.glob == 'John'
    assert mc.glob == 'John'


if __name__ == '__main__':
    test_class_value_usage()
    test_class_property_usage()

    print('All tests finished successfully!')
