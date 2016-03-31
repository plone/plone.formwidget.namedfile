# -*- coding: utf-8 -*-
import doctest
import unittest
from plone.formwidget.namedfile.testing import INTEGRATION_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        layered(doctest.DocFileSuite(
            'widget.rst',
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            encoding='utf-8'),
            layer=INTEGRATION_TESTING),
    )
    return suite
