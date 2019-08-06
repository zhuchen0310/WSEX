# prefer setuptools over distutils
from setuptools import setup, find_packages

# use a consistent encoding
from codecs import open
from os import path
import json
import sys

is_python_2 = sys.version_info < (3, 0)

here = path.abspath(path.dirname(__file__))
root = path.dirname(here)

readme_rst = path.join(here, 'README.rst')
package_json = path.join(here, 'package.json')

# a workaround when installing locally from git repository with pip install -e .
if not path.isfile(package_json):
    package_json = path.join(root, 'package.json')

# long description from README file
with open(readme_rst, encoding='utf-8') as f:
    long_description = f.read()

# version number and all other params from package.json
with open(package_json, encoding='utf-8') as f:
    package = json.load(f)

setup(

    name=package['name'],
    version=package['version'],

    description=package['description'],
    long_description=long_description,

    classifiers=[
        'Development Status :: 1 - Alpha',
        'Intended Audience :: Python Developers',
        'Topic :: Software Development :: Common Library',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Environment :: Console'
    ],

    packages=['wsex'],

    install_requires=[
    ],

    extras_require={
        ':python_version>="3.6.5"': [
        ],
        'qa': [
            'flake8==3.5.0'
        ],
        'doc': [
            'Sphinx==1.7.0'
        ]
    }
)
