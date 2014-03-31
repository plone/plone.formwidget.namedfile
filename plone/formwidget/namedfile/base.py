from Products.CMFCore.utils import getToolByName
try:
    from os import SEEK_END
except ImportError:
    from posixfile import SEEK_END
import urllib

from zope.component import getMultiAdapter
from zope.size import byteDisplay

from z3c.form.interfaces import IDataManager, NOVALUE
from z3c.form.browser import file

from plone.namedfile.utils import safe_basename
from plone.namedfile.interfaces import INamed

from Acquisition import Explicit

from ZPublisher.HTTPRequest import FileUpload


class BaseNamedFileWidget(Explicit, file.FileWidget):

    """A widget for a named file object
    """

    klass = u'named-file-widget'
    value = None  # don't default to a string

    @property
    def allow_nochange(self):
        return not self.ignoreContext and \
            self.field is not None and \
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
            return "%s/%s" % (getToolByName(self.context, 'portal_url')(),
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
            return "%s/++widget++%s/@@download/%s" % (self.request.getURL(),
                                                      self.name,
                                                      self.filename_encoded)
        else:
            return "%s/++widget++%s/@@download" % (self.request.getURL(),
                                                   self.name)

    def action(self):
        action = self.request.get("%s.action" % self.name, "nochange")
        if hasattr(self.form, 'successMessage') and \
                self.form.status == self.form.successMessage:
            # if form action completed successfully, we want nochange
            action = 'nochange'
        return action

    def extract(self, default=NOVALUE):
        action = self.request.get("%s.action" % self.name, None)
        path = self.request.get('PATH_INFO', '')
        if path.endswith('kss_z3cform_inline_validation'):
            action = 'nochange'

        if action == 'remove':
            return None
        elif action == 'nochange':
            if self.ignoreContext:
                return default
            dm = getMultiAdapter((self.context, self.field,), IDataManager)
            # For sub-widgets to function use a query() not get()
            return dm.query(default)

        # empty unnamed FileUploads should not count as a value
        value = super(BaseNamedFileWidget, self).extract(default)
        if isinstance(value, FileUpload):
            value.seek(0, SEEK_END)
            empty = value.tell() == 0
            value.seek(0)
            if empty and not value.filename:
                return default
            value.seek(0)
        return value
