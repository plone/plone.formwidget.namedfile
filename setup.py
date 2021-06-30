# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '2.1.1'

setup(
    name='plone.formwidget.namedfile',
    version=version,
    description="Image widget for z3c.form and Plone",
    long_description=open("README.rst").read() + "\n" +
    open("CHANGES.rst").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone image widget z3c.form',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='https://pypi.org/project/plone.formwidget.namedfile',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['plone', 'plone.formwidget'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.namedfile',
        'plone.z3cform >= 0.7.4',
        'six',
        'z3c.form',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
