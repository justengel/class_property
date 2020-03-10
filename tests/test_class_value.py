

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
    assert SubClass.value == 7
    assert sub.value == 7
    assert mc.value == 7
    assert MyClass.value == 7


if __name__ == '__main__':
    test_import()
    test_class_value()

    print('All tests finished successfully!')
