# -*- coding:utf-8 -*-

# author: Cone
# datetime: 2020-01-10 17:19
# software: PyCharm
from inspect import isclass


def instance(*args, **kwargs):
    def params_instance(cls):
        return cls(*args, **kwargs)  # 带参数的实例
    if args and isclass(args[0]):
        return args[0]()
    return params_instance


if __name__ == '__main__':
    @instance(a=1, b=2)
    class A:
        def __init__(self, a, b):
            print(f"I'm instance of A({a}, {b})")

    @instance
    class B:
        def __init__(self):
            print("I'm instance of B()")
