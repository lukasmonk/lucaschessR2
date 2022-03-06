from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

from Cython.Build import cythonize

setup(ext_modules=cythonize([Extension("FasterCode", ["FasterCode.pyx"], libraries=["irina"], library_dirs=["."])]))
