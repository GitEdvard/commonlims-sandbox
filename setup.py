from setuptools import setup, find_packages

setup(
    name='sandbox',
    version='1.0.0',
    packages=find_packages(exclude=['contrib', 'docs', 'test']),
    entry_points={
                       'console_scripts': [
                           'add-data=commonlims.scripts.add_data:cli_main',
                       ],
                   },
)
