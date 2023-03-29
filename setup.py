#!/usr/bin/env python3

"""
ABISM module instalation script
"""

import setuptools
from abism import __version__


with open('README.md', mode='r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='abism',
    version=__version__,
    scripts=['scripts/abism'],
    author='Julien Girard, Martin Tourneboeuf',
    author_email='tinmarino@gmail.com',
    description=(
        'Adaptative Background Interferometric Strehl Meter\n'
        'Graphical user interface (GUI) '
        'to mesure Astrophysics image quality (Strehl ratio)'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tinmarino/abism',
    packages=[
        'abism',
        'abism.front',
        'abism.back',
        'abism.plugin',
    ],
    install_requires=[
        'matplotlib',  # Image display
        'scipy',  # Interpolation (best square fit)
        'numpy',  # Array calculation
        'astropy',  # Fits parsing, WCS utilities and many surprises
    ],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
