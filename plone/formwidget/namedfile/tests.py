# -*- coding: utf-8 -*-
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from plone.formwidget.namedfile.testing import FUNCTIONAL_TESTING
from plone.formwidget.namedfile.testing import INTEGRATION_TESTING
from plone.formwidget.namedfile.interfaces import IScaleGenerateOnSave
from plone.formwidget.namedfile.datamanager import NamedImageAttributeField
from plone.namedfile.field import NamedImage as NamedImageField
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.scale.storage import AnnotationStorage
from plone.testing import layered
from plone.namedfile.tests import getFile
from z3c.form.interfaces import IDataManager
from ZPublisher.pubevents import PubSuccess
from zope.annotation import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import implementer

import doctest
import re
import six
import unittest


class IHasImage(IImageScaleTraversable):
    image = NamedImageField()


@implementer(IAttributeAnnotatable, IHasImage)
class DummyContent(SimpleItem):
    image = None
    modified = DateTime
    id = __name__ = "item"
    title = "foo"

    def Title(self):
        return self.title


class ScaleGenerateOnSaveTests(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        item = DummyContent()
        self.layer["app"]._setOb("item", item)
        self.item = self.layer["app"].item
        self.request = self.layer["request"]

    def test_not_generate_scales_on_save(self):
        self.assertEqual(len(AnnotationStorage(self.item).storage), 0)
        dm = getMultiAdapter((self.item, IHasImage["image"]), IDataManager)
        self.assertIsInstance(dm, NamedImageAttributeField)
        self.assertFalse(dm.scale_generate_on_save)
        dm.set(NamedImage(getFile("image.png"), "image/png", "image.png"))
        self.assertFalse(IScaleGenerateOnSave.providedBy(self.request))
        notify(PubSuccess(self.request))
        self.assertEqual(len(AnnotationStorage(self.item).storage), 0)

    def test_generate_scales_on_save(self):
        self.assertEqual(len(AnnotationStorage(self.item).storage), 0)
        dm = getMultiAdapter((self.item, IHasImage["image"]), IDataManager)
        self.assertIsInstance(dm, NamedImageAttributeField)
        self.assertFalse(dm.scale_generate_on_save)
        dm.scale_generate_on_save = True
        dm.set(NamedImage(getFile("image.png"), "image/png", "image.png"))
        self.assertTrue(IScaleGenerateOnSave.providedBy(self.request))
        notify(PubSuccess(self.request))
        self.assertGreater(len(AnnotationStorage(self.item).storage), 0)


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
    suite.addTest(unittest.makeSuite(ScaleGenerateOnSaveTests))
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
