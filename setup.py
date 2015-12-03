from setuptools import setup, find_packages


setup(
    name='atoll',
    version='0.0.1',
    description='data analysis pipelines',
    url='https://github.com/coralproject/atoll',
    author='The Coral Project',
    license='MIT',

    packages=find_packages(),
    install_requires=[
        'six',
        'flask',
        'joblib',
        'celery',
        'requests',
    ],
    test_requires=[
        'nose',
        'httpretty'
    ],
    test_suite='nose.collector',
)
