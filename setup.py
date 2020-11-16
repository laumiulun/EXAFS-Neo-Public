# coding: utf-8
from __future__ import print_function, unicode_literals
import sys
import codecs
from setuptools import setup, find_packages
from exafs import __version__, __author__, __email__


with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]


def long_description():
    with codecs.open('README.md', 'rb') as readme:
        if not sys.version_info < (3, 0, 0):
            return readme.read().decode('utf-8')


setup(
    name='exafs',
    version=__version__,
    packages=find_packages(),

    author=__author__,
    author_email=__email__,
    keywords=['exafs', 'AI', 'analysis'],
    description='exafs AI analysis using GA',
    long_description=long_description(),
    url='https://github.com/laumiulun/EXAFS_Neo',
    download_url='https://github.com/laumiulun/EXAFS_Neo/tarball/master',
    include_package_data=True,
    zip_safe=False,

    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'exafs = exafs.exafs:main',
        ]
    },
    license='GPLv3',
)
