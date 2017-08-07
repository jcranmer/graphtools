
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='graphtools',
    version='0.0.1',
    description='Graph tools',
    url='https://github.com/jcranmer/graphtools',
    author='Joshua Cranmer',

    # XXX: License, classifiers, ...

    py_modules=['graphmaker'],

    entry_points={
        'console_scripts': [
            'graphmaker=graphmaker:main',
        ],
    },
)


