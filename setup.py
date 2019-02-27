from setuptools import setup, find_packages

requirements = ['flask', 'unidecode']

setup(
    name='runeverywhere',
    version='0.1.0',
    description='',
    url='https://github.com/msimms/RunEverywhere',
    author='Mike Simms',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=requirements,
)
