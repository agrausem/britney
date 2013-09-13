#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    lines = requirements.readlines()
    libraries = [lib for lib in lines if not lib.startswith('-')]
    dependency_links = [link.split()[1] for link in lines if 
            link.startswith('-f')]

setup(
    name='britney',
    version='0.1',
    author='Arnaud Grausem',
    author_email='arnaud.grausem@gmail.com',
    maintainer='Arnaud Grausem',
    maintainer_email='arnaud.grausem@gmail.com',
    url='https://github.com/agrausem/britney',
    license='PSF',
    description=u'Python implementation of SPORE',
    long_description=long_description,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    download_url='http://pypi.python.org/pypi/britney',
    install_requires=libraries,
    dependency_links=dependency_links,
    keywords=['SPORE', 'REST Api', 'client'],
    entry_points={},
    classifiers = (
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    )
)
