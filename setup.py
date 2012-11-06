#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


setup(
    name='django-compress',
    version='1.0.0',
    description='A Django app for compressing CSS and JS',
    author='Michael Crute',
    author_email='mike@finiteloopsoftware.com',
    url='http://github.com/finiteloopsoftware/django-compress/',
    long_description=open('README.rst', 'r').read(),
    packages=[
        'compress',
        'compress.templatetags',
    ],
    package_data={
        'compress': ['templates/compress/*'],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
