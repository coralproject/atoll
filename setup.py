from atoll import __version__
from setuptools import setup, find_packages

setup(
    name='atoll',
    version=__version__,
    description='data analysis pipelines',
    url='https://github.com/coralproject/atoll',
    author='The Coral Project',
    license='MIT',

    packages=find_packages(),
    install_requires=[
        'flask',
        'joblib',
        'requests',
    ],
)
