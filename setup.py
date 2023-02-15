
from setuptools import setup, find_packages

NAME = 'bonesis'
VERSION = '9999'

setup(name=NAME,
    version=VERSION,
    description = "Synthesis of Most Permissive Boolean Networks",
    license_files = ('LICENSE.txt', 'Licence_CeCILL_V2.1-fr.txt'),
    install_requires = [
        "boolean.py",
        "clingo>=5.5",
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

