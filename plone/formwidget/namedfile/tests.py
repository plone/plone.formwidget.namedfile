# -*- coding: utf-8 -*-
from z3c.form import testing
import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'widget.rst',
            setUp=testing.setUp,
            tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        ),
    ))
