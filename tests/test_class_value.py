

def test_import():
    from class_property import class_value, class_property


def test_class_value():
    from class_property import class_value

    @class_value.decorate
    class MyClass(object):
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
    assert SubClass.value == 7, SubClass.value
    assert sub.value == 7, sub.value
    assert mc.value == 7, mc.value
    assert MyClass.value == 7, MyClass.value


def test_class_value_inhertance():
    from class_property import class_value

    class MyClass(object, metaclass=class_value.metaclass()):
        value = class_value(1)

    class SubClass(MyClass):
        value = 2

    mc = MyClass
    sub = SubClass()
    sub.value = 7
    assert SubClass.value == 7, SubClass.value
    assert sub.value == 7, sub.value
    assert mc.value == 7, mc.value
    assert MyClass.value == 7, MyClass.value


if __name__ == '__main__':
    test_import()
    test_class_value()
    test_class_value_inhertance()

    print('All tests finished successfully!')
