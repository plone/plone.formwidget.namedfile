from setuptools import setup


version = "4.0.0a2.dev0"

setup(
    name="plone.formwidget.namedfile",
    version=version,
    description="Image widget for z3c.form and Plone",
    long_description=open("README.rst").read() + "\n" + open("CHANGES.rst").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone image widget z3c.form",
    author="Martin Aspeli",
    author_email="optilude@gmail.com",
    url="https://pypi.org/project/plone.formwidget.namedfile",
    license="GPL",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "plone.base",
        "plone.namedfile>=6.3.0",
        "Products.MimetypesRegistry",
        "plone.registry",
        "z3c.form",
        "Zope",
    ],
    extras_require={
        "test": [
            "Pillow",
            "plone.app.testing",
            "plone.scale",
            "plone.testing",
            "zope.pagetemplate",
        ],
    },
)
