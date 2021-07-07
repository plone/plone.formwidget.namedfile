# -*- coding: utf-8 -*-
from plone.formwidget.namedfile.interfaces import IScaleGenerateOnSave
from plone.formwidget.namedfile.utils import get_scale_infos
from plone.namedfile.field import INamedImageField
from z3c.form.datamanager import AttributeField
from ZODB.POSException import ConflictError
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import Interface
from zope.interface import alsoProvides

import logging
import os
import transaction


ANNOTATION_KEY = "plone.formwidget.namedfile.scale"
ENVIRONMENT_KEY = "PLONE_SCALE_GENERATE_ON_SAVE"

logger = logging.getLogger(__name__)


@adapter(Interface, INamedImageField)
class NamedImageAttributeField(AttributeField):

    scale_generate_on_save = (
        os.environ.get(ENVIRONMENT_KEY) or ""
    ).lower() in ["1", "true", "yes", "on"]

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        super(NamedImageAttributeField, self).set(value)
        if self.scale_generate_on_save:
            schedule_plone_scale_generate_on_save(
                self.context, getRequest(), self.field.__name__)


def schedule_plone_scale_generate_on_save(context, request, fieldname):
    annotations = IAnnotations(request, {})
    annotations.setdefault(ANNOTATION_KEY, [])
    annotations[ANNOTATION_KEY].append((context, fieldname))
    alsoProvides(request, IScaleGenerateOnSave)


def plone_scale_generate_on_save(event):
    if not IScaleGenerateOnSave.providedBy(event.request):
        return
    annotations = IAnnotations(event.request, {})
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
