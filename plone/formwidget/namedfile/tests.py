from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from ZPublisher.pubevents import PubSuccess
from plone.formwidget.namedfile.datamanager import NamedImageAttributeField
from plone.formwidget.namedfile.interfaces import IScaleGenerateOnSave
from plone.formwidget.namedfile.testing import FUNCTIONAL_TESTING
from plone.formwidget.namedfile.testing import INTEGRATION_TESTING
from plone.namedfile.field import NamedImage as NamedImageField
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.tests import getFile
from plone.scale.storage import AnnotationStorage
from plone.testing import layered
from z3c.form.interfaces import IDataManager
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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ScaleGenerateOnSaveTests))
    suite.addTest(
        layered(
            doctest.DocFileSuite(
                "widget.rst",
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                encoding="utf-8",
            ),
            layer=INTEGRATION_TESTING,
        ),
    )
    return suite
