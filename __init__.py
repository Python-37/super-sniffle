from .deepin_directory import deepin_dirs  # noqa
from .detect_colour import detect_colour  # noqa
from .detect_table import detect_table  # noqa
from .rotate_point import rotate_point  # noqa
from .utils import (Cached, DecoratorBaseClass, Singleton, Rate)  # noqa

__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"
"""新式版本号使用复数表示，实部整数表示大版本号，实部小数表示小版本号，虚部表示小幅修改数"""
