__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import types
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable
from weakref import WeakValueDictionary


class Singleton(type):
    """
    单例类元类
    不要动这个类和以这个类为元类的类的源码
    """
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class Cached(type):
    """
    同参单例类元类，如果创建实例提供的参数相同，则返回旧有保存的实例
    不要动这个类和以这个类为元类的类的源码
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cache = WeakValueDictionary()

    def __call__(self, *args):
        if args in self.__cache:
            return self.__cache[args]
        else:
            obj = super().__call__(*args)
            self.__cache[args] = obj
            return obj


class CachedCls(metaclass=Cached):
    """使用自定义元类的写法"""
    pass


class DecoratorBaseClass(ABC):
    """装饰器类基类，因为装饰器类都需要定义同样的 __get__ 方法，就索性写在父类里
    """
    @abstractmethod
    def __init__(self, func):
        """必须在子类中实现这个方法，因为这是装饰器类必需的方法"""
        wraps(func)(self)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """必须在子类中实现这个方法，因为这是装饰器类必需的方法"""
        res = self.__wrapped__(*args, **kwargs)
        return res

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)


class Rate(object):
    """表示比率数值的属性描述符，在类中作为类属性使用，只允许该属性设定为0~1的数
    """
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not any((isinstance(value, float), isinstance(value, int))):
            raise TypeError("必须提供一个介于0和1之间的小数")
        if not 0 <= value <= 1:
            raise ValueError("必须提供一个介于0和1之间的小数")
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


class PositiveInt(object):
    """属性描述符，表示只接受正整数"""
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError("必须提供一个正整数")
        if value < 0:
            raise ValueError("必须提供一个正整数")
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


class lazyproperty_cls:
    """
    延迟计算属性描述符类
    """
    def __init__(self, func: Callable):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


def lazyproperty(func: Callable):
    """
    延迟计算属性装饰器，可以避免属性被变更
    """
    name = '_lazy_' + func.__name__

    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value

    return lazy
