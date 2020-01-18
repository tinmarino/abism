import setuptools



with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='abism',
    version='0.902',
    scripts=['abism.py'] ,
    author='Julien Girard, Martin Tourneboeuf',
    author_email='tinmarino@gmail.com',
    description='GUI to mesure astrofisics image quality',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tinmarino/abism",
    packages=['abism',
              'abism.front',
              'abism.back',
              'abism.plugin',
              ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
     ],
 )
