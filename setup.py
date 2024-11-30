from setuptools import find_packages, setup

setup(
    name='aoc-tools',
    description='my aoc tooling',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['aoc=aoc.cli:main'],
    },
)