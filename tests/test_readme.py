
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


def test_change_from_value_to_property():
    from class_property import class_value, class_property


    class MyClass(object, metaclass=class_value.metaclass()):
        value = class_value(1)


    class SubClass(MyClass):
        _VALUE = 2

        # This replaces "MyClass.value". class_value/class_property uses the metaclass, so we have to replace.
        # We can only change to a new object if we change the metaclass.
        @class_property
        def value(self):
            return SubClass._VALUE

        @value.setter
        def value(self, val):
            SubClass._VALUE = val


    class SetValueClass(MyClass):
        value = 3


    # Check that SetValueClass just changes the current value
    assert MyClass.value == 3
    assert SubClass.value == 3
    assert SetValueClass.value == 3

    mc = MyClass()
    mc.value = 4

    sub = SubClass()
    sub.value = 7
    assert sub.value == 7
    assert SubClass.value == 7
    assert SubClass._VALUE == 7

    # MyClass.value is the new class_property from SubClass, because of the shared metaclass
    assert mc.value == 7
    assert MyClass.value == 7
    assert SetValueClass.value == 7


def test_change_property_disconnect():
    from class_property import class_property


    class MyClass(object, metaclass=class_property.metaclass()):
        _VALUE1 = 1

        @class_property
        def value(self):
            return MyClass._VALUE1

        @value.setter
        def value(self, val):
            MyClass._VALUE1 = val


    class SubClass(MyClass, metaclass=class_property.metaclass(MyClass)):
        _VALUE2 = 2

        # Because we have a different metaclass `SubClass.value` is different from `MyClass.value`
        @class_property
        def value():
            return SubClass._VALUE2

        @value.setter
        def value(val):
            SubClass._VALUE2 = val


    mc = MyClass()
    mc.value = 4

    # SubClass.value is using a different metaclass and is disconnected from MyClass
    sub = SubClass()
    sub.value = 7
    assert sub.value == 7
    assert SubClass.value == 7
    assert SubClass._VALUE2 == 7

    # MyClass.value is using a different metaclass and is disconnected from SubClass
    assert mc.value == 4
    assert MyClass.value == 4
    assert MyClass._VALUE1 == 4


if __name__ == '__main__':
    test_class_value_usage()
    test_class_property_usage()

    test_change_from_value_to_property()
    test_change_property_disconnect()

    print('All tests finished successfully!')
