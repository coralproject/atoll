from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='atoll',
    version='0.0.1',
    description='data analysis pipelines',
    url='https://github.com/coralproject/atoll',
    author='The Coral Project',
    license='MIT',

    packages=find_packages(),
    install_requires=required,
    test_requires=[
        'nose',
        'httpretty'
    ],
    test_suite='nose.collector',
)
