# -*- coding: utf-8 -*-
from plone.formwidget.namedfile.interfaces import IScaleGenerateOnSave
from plone.namedfile.field import INamedImageField
from z3c.form.datamanager import AttributeField
from ZODB.POSException import ConflictError
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import Interface
from zope.interface import alsoProvides

import logging
import os
import transaction

try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE_5 = False  # pragma: no cover
else:
    PLONE_5 = True  # pragma: no cover


ANNOTATION_KEY = "plone.formwidget.namedfile.scale"
ENVIRONMENT_KEY = "PLONE_SCALE_GENERATE_ON_SAVE"

logger = logging.getLogger(__name__)


@adapter(Interface, INamedImageField)
class NamedImageAttributeField(AttributeField):

    def __init__(self, *args, **kwargs):
        super(NamedImageAttributeField, self).__init__(*args, **kwargs)
        flag = (os.environ.get(ENVIRONMENT_KEY) or "").lower()
        self.scale_generate_on_save = flag in ["1", "true", "yes", "on"]

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        super(NamedImageAttributeField, self).set(value)
        if self.scale_generate_on_save:
            schedule_plone_scale_generate_on_save(
                self.context, getRequest(), self.field.__name__)


def schedule_plone_scale_generate_on_save(context, request, fieldname):
    annotations = IAnnotations(request, None)
    if annotations is not None:
        annotations.setdefault(ANNOTATION_KEY, [])
        annotations[ANNOTATION_KEY].append((context, fieldname))
        alsoProvides(request, IScaleGenerateOnSave)


def plone_scale_generate_on_save(event):
    if not IScaleGenerateOnSave.providedBy(event.request):
        return
    annotations = IAnnotations(event.request, None)
    if annotations is None:
        return
    for context, fieldname in annotations.get(ANNOTATION_KEY) or []:
        try:
            images = getMultiAdapter((context, event.request), name="images")
            try:
                scales = get_scale_infos()
            except ImportError:
                continue
            t = transaction.get()
            for name, actual_width, actual_height in scales:
                images.scale(fieldname, scale=name)
            image = getattr(context, fieldname, None)
            if image:  # REST API requires this scale to refer the original
                width, height = image.getImageSize()
                images.scale(fieldname,
                             width=width, height=height, direction="thumbnail")
            msg = "/".join(filter(bool, ["/".join(context.getPhysicalPath()),
                                         "@@images", fieldname]))
            t.note(msg)
            t.commit()
        except ConflictError:
            msg = "/".join(filter(bool, ["/".join(context.getPhysicalPath()),
                                         "@@images", fieldname]))
            logger.warning("ConflictError. Scale not generated on save: " + msg)


def get_scale_infos():
    """Returns a list of (name, width, height) 3-tuples of the
    available image scales.
    """
    from Products.CMFCore.interfaces import IPropertiesTool
    if PLONE_5:
        from plone.registry.interfaces import IRegistry

        registry = getUtility(IRegistry)
        from Products.CMFPlone.interfaces import IImagingSchema

        imaging_settings = registry.forInterface(IImagingSchema, prefix="plone")
        allowed_sizes = imaging_settings.allowed_sizes

    else:
        ptool = getUtility(IPropertiesTool)
        image_properties = ptool.imaging_properties
        allowed_sizes = image_properties.getProperty("allowed_sizes")

    def split_scale_info(allowed_size):
        name, dims = allowed_size.split(" ")
        width, height = list(map(int, dims.split(":")))
        return name, width, height

    return [split_scale_info(size) for size in allowed_sizes]
