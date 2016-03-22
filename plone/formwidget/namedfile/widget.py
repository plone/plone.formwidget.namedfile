# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import Explicit
from plone.formwidget.namedfile.converter import b64decode_file
from plone.formwidget.namedfile.interfaces import INamedFileWidget
from plone.formwidget.namedfile.interfaces import INamedImageWidget
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import INamed
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImage
from plone.namedfile.interfaces import INamedImageField
from plone.namedfile.utils import safe_basename
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.MimetypesRegistry.common import MimeTypeException
from z3c.form.browser import file
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import implements
from zope.interface import implementsOnly
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.schema.interfaces import IASCII
from zope.size import byteDisplay
from ZPublisher.HTTPRequest import FileUpload
import urllib

try:
    from os import SEEK_END
except ImportError:
    from posixfile import SEEK_END


def _make_namedfile(value, field, widget):
    """Return a NamedImage or NamedFile instance, if it isn't already one -
    e.g. when it's base64 encoded data.
    """
    if isinstance(value, basestring) and IASCII.providedBy(field):
        filename, data = b64decode_file(value)
        if INamedImageWidget.providedBy(widget):
            value = NamedImage(data=data, filename=filename)
        else:
            value = NamedFile(data=data, filename=filename)
    return value


class NamedFileWidget(Explicit, file.FileWidget):
    """A widget for a named file object
    """
    implementsOnly(INamedFileWidget)

    klass = u'named-file-widget'
    value = None  # don't default to a string

    @property
    def allow_nochange(self):
        return self.field is not None and \
            self.value is not None and \
            self.value != self.field.missing_value

    @property
    def filename(self):
        if self.field is not None and self.value == self.field.missing_value:
            return None
        elif INamed.providedBy(self.value):
            return self.value.filename
        elif isinstance(self.value, FileUpload):
            return safe_basename(self.value.filename)
        else:
            return None

    @property
    def file_size(self):
        if INamed.providedBy(self.value):
            return byteDisplay(self.value.getSize())
        else:
            return "0 KB"

    @property
    def _mimetype(self):
        registry = getToolByName(self.context, 'mimetypes_registry', None)
        if not registry:
            return None
        try:
            content_type = self.value.contentType
            mimetypes = registry.lookup(content_type)
        except AttributeError:
            mimetypes = [registry.lookupExtension(self.filename)]
        except MimeTypeException:
            return None

        if len(mimetypes):
            return mimetypes[0]
        else:
            return None

    @property
    def file_content_type(self):
        if not self.value:
            return ""

        mimetype = self._mimetype
        if mimetype:
            return mimetype.name()
        else:
            return getattr(self.value, 'contentType', None)

    @property
    def file_icon(self):
        if not self.value:
            return None

        mimetype = self._mimetype
        if mimetype and mimetype.icon_path:
            return "%s/%s" % (getToolByName(getSite(), 'portal_url')(),
                              mimetype.icon_path)
        else:
            return None

    @property
    def filename_encoded(self):
        filename = self.filename
        if filename is None:
            return None
        else:
            if isinstance(filename, unicode):
                filename = filename.encode('utf-8')
            return urllib.quote_plus(filename)

    @property
    def download_url(self):
        if self.field is None:
            return None
        if self.ignoreContext:
            return None
        if self.filename_encoded:
            return "%s/++widget++%s/@@download/%s" % (
                self.request.getURL(), self.name, self.filename_encoded)
        else:
            return "%s/++widget++%s/@@download" % (
                self.request.getURL(), self.name)

    def action(self):
        action = self.request.get("%s.action" % self.name, "nochange")
        if hasattr(self.form, 'successMessage')\
                and self.form.status == self.form.successMessage:
            # if form action completed successfully, we want nochange
            action = 'nochange'
        return action

    def extract(self, default=NOVALUE):
        action = self.request.get("%s.action" % self.name, None)
        if self.request.get(
                'PATH_INFO', '').endswith('kss_z3cform_inline_validation'):
            action = 'nochange'

        if action == 'remove':
            return None
        elif action == 'nochange':
            if self.value is not None:
                return self.value
            if self.ignoreContext:
                return default
            dm = getMultiAdapter((self.context, self.field,), IDataManager)
            # For sub-widgets to function use a query() not get()
            data = dm.query(default)
            data = _make_namedfile(data, self.field, self.context)
            return data

        # empty unnamed FileUploads should not count as a value
        value = super(NamedFileWidget, self).extract(default)
        if isinstance(value, FileUpload):
            value.seek(0, SEEK_END)
            empty = value.tell() == 0
            value.seek(0)
            if empty and not value.filename:
                return default
            value.seek(0)
        return value


class NamedImageWidget(NamedFileWidget):
    """A widget for a named file object
    """
    implementsOnly(INamedImageWidget)

    klass = u'named-image-widget'

    @property
    def width(self):
        if INamedImage.providedBy(self.value):
            return self.value._width
        else:
            return None

    @property
    def height(self):
        if INamedImage.providedBy(self.value):
            return self.value._height
        else:
            return None

    @property
    def thumb_tag(self):
        """ Return a img tag with a url to the preview scale and the width and
            height of a thumbnail scale.

            This way on retina screens the image is displayed in screen pixels.
            On non-retina screens the browser will downsize them as used to.
        """
        try:
            scales = getMultiAdapter(
                (self.context, self.request), name='images')
        except ComponentLookupError:
            # For example in the @@site-controlpanel after uploading an image,
            # because the context is a RecordsProxy.
            return u''
        fieldname = self.field.getName()
        thumb_scale = scales.scale(fieldname, scale='thumb')
        preview_scale = scales.scale(fieldname, scale='preview')
        if preview_scale is not None and thumb_scale is not None:
            return preview_scale.tag(width=thumb_scale.width,
                                     height=thumb_scale.height)
        return u''

    @property
    def alt(self):
        return self.title


class Download(BrowserView):
    """Download a file, via ../context/form/++widget++/@@download/filename
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.filename = None

    def publishTraverse(self, request, name):

        if self.filename is None:  # ../@@download/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)

        return self

    def __call__(self):
        # TODO: Security check on form view/widget

        if self.context.ignoreContext:
            raise NotFound(
                "Cannot get the data file from a widget with no context")

        if self.context.form is not None:
            content = aq_inner(self.context.form.getContent())
        else:
            content = aq_inner(self.context.context)
        field = aq_inner(self.context.field)

        dm = getMultiAdapter((content, field,), IDataManager)
        file_ = dm.get()
        file_ = _make_namedfile(file_, field, self.context)

        if file_ is None:
            raise NotFound(self, self.filename, self.request)

        if not self.filename:
            self.filename = getattr(file_, 'filename', None)

        set_headers(file_, self.request.response, filename=self.filename)
        return stream_data(file_)


@implementer(IFieldWidget)
@adapter(INamedFileField, IFormLayer)
def NamedFileFieldWidget(field, request):
    return FieldWidget(field, NamedFileWidget(request))


@implementer(IFieldWidget)
@adapter(INamedImageField, IFormLayer)
def NamedImageFieldWidget(field, request):
    return FieldWidget(field, NamedImageWidget(request))
