#!/usr/bin/env python

from setuptools import setup, find_packages
import codecs

setup(
    name='celerytest',
    version='0.1.0',
    author=u'Willem Bult',
    author_email='willem.bult@gmail.com',
    packages=find_packages(),
    url='http://github.com/RentMethod/celerytest',
    license='BSD license, see LICENSE',
    description='Test functions to use for tests that depend on the execution of Celery tasks',
    long_description=codecs.open('README.md', 'r', 'utf-8').read(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'celery==3.0.19'
    ],
    test_suite='celerytest.tests'
)
