'''
ps_killer setup module
'''

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='ps_killer',
    version='0.0.1',
    description='A ps killer GUI',
    url='https://github.com/andrew222/ps_killer',
    author='Andrew Yang',
    author_email='zzcv20051122@gmail.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 1 - Alpha'
    ],

    keywords='GUI ps manager',
    packages=find_packages(),
    install_requires=['psutil', 'apscheduler'],
    extras_require={},
    package_data={},

    entry_points={
        'console_scripts': [
            'ps_killer=ps_killer:__main__',
        ],
    },
)
