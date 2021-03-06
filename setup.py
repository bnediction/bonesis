
from setuptools import setup, find_packages

NAME = 'bonesis'
VERSION = '9999'

setup(name=NAME,
    version=VERSION,
    description = "Synthesis of Most Permissive Boolean Networks",
    install_requires = [
        "boolean.py",
        "clingo",
        "colomoto_jupyter",
        "mpbn>=1.7",
        "networkx",
        "numpy",
        "pandas",
        "scipy",
    ],
    entry_points = {
        "console_scripts": [
            "bonesis-utils=bonesis.cli:main_utils",
            "bonesis-reprogramming=bonesis.cli:main_reprogramming",
            "bonesis-attractors=bonesis.cli:main_attractors",
        ],
    },
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords="computational systems biology",
    packages = find_packages(),
    package_data = {"bonesis0": ['*.cfg']}
)

