import setuptools
from abism import __version__


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='abism',
    version=__version__,
    scripts=['scripts/abism'],
    author='Julien Girard, Martin Tourneboeuf',
    author_email='tinmarino@gmail.com',
    description='GUI to mesure astrofisics image quality',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tinmarino/abism",
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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
