

def test_import():
    from class_property import metaclass, decorate, class_value, class_property


def test_class_property():
    from class_property import class_property

    @class_property.decorate
    class MyClass(object):
        _A = None
        _B = None

        @class_property
        def value(self):
            return MyClass._A

        @value.setter
        def value(self, value):
            MyClass._A = value

        @class_property
        def no_arg():
            return MyClass._B

        @no_arg.setter
        def no_arg(value):
            MyClass._B = value

    # ===== Test normal property with value =====
    mc = MyClass()
    assert MyClass.value is None
    assert mc.value is None

    MyClass.value = 1
    assert MyClass.value == 1
    assert mc.value == 1

    mc.value = 2
    assert MyClass.value == 2
    assert mc.value == 2

    # ===== Test no arg property with value =====
    assert MyClass.no_arg is None
    assert mc.no_arg is None

    MyClass.no_arg = 15
    assert MyClass.no_arg == 15
    assert mc.no_arg == 15

    mc.no_arg = 37
    assert MyClass.no_arg == 37
    assert mc.no_arg == 37


def test_call():
    import class_property

    class MyClass(object, metaclass=class_property.metaclass()):
        _VALUE = None

        @class_property
        def value(self):
            return MyClass._VALUE

        @value.setter
        def value(self, value):
            MyClass._VALUE = value

    # ===== Test normal property with value =====
    mc = MyClass()
    assert MyClass.value is None
    assert mc.value is None

    MyClass.value = 1
    assert MyClass.value == 1
    assert mc.value == 1

    mc.value = 2
    assert MyClass.value == 2
    assert mc.value == 2


def test_class_property_inheritance():
    from class_property import class_property

    class MyClass(object, metaclass=class_property.metaclass()):
        _value = None

        @class_property
        def value(self):
            return MyClass._value

        @value.setter
        def value(self, val):
            MyClass._value = val


    class SubClass(MyClass):
        value = 2

    mc = MyClass
    sub = SubClass()
    sub.value = 7
    assert SubClass.value == 7, SubClass.value
    assert sub.value == 7, sub.value
    assert mc.value == 7, mc.value
    assert MyClass.value == 7, MyClass.value


def test_class_value_inherit_class_property():
    from class_property import class_value, class_property

    class MyClass(object, metaclass=class_value.metaclass()):
        value = class_value(1)

    class SubClass(MyClass):
        _VALUE = None

        # This replaces "MyClass.value". class_value/class_property uses the metaclass, so we have to replace.
        # We can only change to a new object if we change the metaclass.
        @class_property
        def value(self):
            return SubClass._VALUE

        @value.setter
        def value(self, val):
            SubClass._VALUE = val

    mc = MyClass()

    sub = SubClass()
    sub.value = 7
    assert sub.value == 7, sub.value
    assert SubClass.value == 7, SubClass.value
    assert SubClass._VALUE == 7, SubClass._VALUE

    assert mc.value == 7, mc.value
    assert MyClass.value == 7, MyClass.value


def test_class_value_inherit_class_property_new_metaclass():
    from class_property import class_value, class_property

    class MyClass(object, metaclass=class_value.metaclass()):
        value = class_value(1)

    class SubClass(MyClass, metaclass=class_property.metaclass(MyClass)):
        _VALUE = None

        # This replaces "MyClass.value". class_value/class_property uses the metaclass, so we have to replace.
        # We can only change to a new object if we change the metaclass.
        @class_property
        def value(self):
            return SubClass._VALUE

        @value.setter
        def value(self, val):
            SubClass._VALUE = val

    mc = MyClass()
    mc.value = 2

    sub = SubClass()
    sub.value = 7
    assert sub.value == 7, sub.value
    assert SubClass.value == 7, SubClass.value
    assert SubClass._VALUE == 7, SubClass._VALUE

    assert mc.value == 2, mc.value
    assert MyClass.value == 2, MyClass.value


if __name__ == '__main__':
    test_import()
    test_class_property()
    test_call()

    test_class_property_inheritance()
    test_class_value_inherit_class_property()
    test_class_value_inherit_class_property_new_metaclass()

    print('All tests finished successfully!')
