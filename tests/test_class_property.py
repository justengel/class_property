

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


if __name__ == '__main__':
    test_import()
    test_class_property()
    test_call()

    print('All tests finished successfully!')
