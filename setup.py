from setuptools import setup
from setuptools import find_packages

version = '1.0.13'

setup(
    name='plone.formwidget.namedfile',
    version=version,
    description="Image widget for z3c.form and Plone",
    long_description=open("README.rst").read() + "\n" +
    open("CHANGES.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone image widget z3c.form',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='http://pypi.python.org/pypi/plone.formwidget.namedfile',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.formwidget'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.namedfile',
        'plone.z3cform >= 0.7.4',
        'z3c.form',
    ],
    extras_require={
        'test': ['z3c.form [test]'],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
