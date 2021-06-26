from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = ['flax', 'jax']

setup(
    name='jax_flax_trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='JAX/FLAX model training application.'
)
