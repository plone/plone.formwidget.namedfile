from z3c.form import testing
from zope.testing.doctestunit import DocFileSuite
import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        DocFileSuite(
            'widget.rst',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        ),
    ))
