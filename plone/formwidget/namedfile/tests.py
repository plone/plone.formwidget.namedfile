# -*- coding: utf-8 -*-
from plone.formwidget.namedfile.testing import INTEGRATION_TESTING
from plone.testing import layered

import doctest
import re
import six
import unittest


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            got = re.sub('zope.publisher.interfaces.NotFound', 'NotFound', got)
            got = re.sub("u'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        layered(doctest.DocFileSuite(
            'widget.rst',
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            encoding='utf-8',
            checker=Py23DocChecker(),
            ),
            layer=INTEGRATION_TESTING),
    )
    return suite
