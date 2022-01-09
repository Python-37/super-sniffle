import numpy as np
from setuptools import Extension, setup

fib_ext = Extension("demo", ["extension_types.pyx"])
setup(ext_modules=[fib_ext], include_dirs=[np.get_include()])
