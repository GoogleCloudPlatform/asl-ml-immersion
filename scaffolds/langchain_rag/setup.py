""" Setup for pip install -e .
"""

from setuptools import find_packages, setup

REQS = None
with open("requirements.txt", encoding="utf-8") as fp:
    REQS = [req.strip() for req in fp.readlines()]

setup(
    name="app",
    version="0.1",
    packages=find_packages(),
    install_requires=REQS,
)
