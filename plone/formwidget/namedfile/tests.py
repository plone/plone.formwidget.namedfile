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
            got = re.sub('NotFound', 'zope.publisher.interfaces.NotFound', got)
            got = re.sub('InvalidState', 'plone.formwidget.namedfile.validator.InvalidState', got)
            got = re.sub('RequiredMissing', 'zope.schema._bootstrapinterfaces.RequiredMissing', got)
            got = re.sub('IOError: cannot identify image file', 'OSError: cannot identify image file', got)
            got = re.sub('IO instance', 'IO object', got)
            got = re.sub("u'(.*?)'", "'\\1'", got)
            got = re.sub('u"(.*?)"', '"\\1"', got)
            got = re.sub("b'(.*?)'", "'\\1'", got)
            got = re.sub('b"(.*?)"', '"\\1"', got)
            want = re.sub("u'(.*?)'", "'\\1'", want)
            want = re.sub('u"(.*?)"', '"\\1"', want)
            want = re.sub("b'(.*?)'", "'\\1'", want)
            want = re.sub('b"(.*?)"', '"\\1"', want)
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
