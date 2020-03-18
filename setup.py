
from setuptools import setup, find_packages

NAME = 'bonesis'
VERSION = '9999'

setup(name=NAME,
    version=VERSION,
    description = "Synthesis of Most Permissive Boolean Networks",
    install_requires = [
        "boolean.py",
        "colomoto_jupyter",
        "networkx",
        "numpy",
        "pandas",
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords="computational systems biology",

    include_package_data = True,
    packages = find_packages()
)

