from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        name="cython_levenshtein",  # Give it a specific name, matching the .pyx file
        sources=["cython_levenshtein.pyx"],  # List .pyx file explicitly
        include_dirs=[numpy.get_include()]  # Include NumPy headers
    ),
]

setup(
    name="Levenshtein",
    ext_modules=cythonize(extensions),
)