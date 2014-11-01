#!/usr/bin/env python
from setuptools import setup, find_packages

# convert the readme to pypi compatible rst
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name='celerytest',
    version='0.1.1',
    author=u'Willem Bult',
    author_email='willem.bult@gmail.com',
    packages=find_packages(),
    url='http://github.com/RentMethod/celerytest',
    download_url='https://github.com/RentMethod/celerytest/archive/0.1.1.tar.gz',
    keywords=['celery','testing','integration','test'],
    license='BSD license, see LICENSE',
    description='Run a monitored Celery worker for integration tests that depend on Celery tasks',
    long_description=read_md('README.md'),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'celery==3.0.19'
    ],
    test_suite='celerytest.tests'
)
