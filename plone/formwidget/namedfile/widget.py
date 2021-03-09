from Acquisition import aq_inner
from Acquisition import Explicit
from datetime import datetime
from os import SEEK_END
from persistent.dict import PersistentDict
from plone.formwidget.namedfile import utils
from plone.formwidget.namedfile.converter import b64decode_file
from plone.formwidget.namedfile.interfaces import IFileUploadTemporaryStorage
from plone.formwidget.namedfile.interfaces import INamedFileWidget
from plone.formwidget.namedfile.interfaces import INamedImageWidget
from plone.namedfile.browser import Download as DownloadBase
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import INamed
from plone.namedfile.interfaces import INamedBlobFileField
from plone.namedfile.interfaces import INamedBlobImageField
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImage
from plone.namedfile.interfaces import INamedImageField
from plone.namedfile.utils import safe_basename
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.MimetypesRegistry.interfaces import MimeTypeException
from z3c.form.browser.file import FileWidget
from z3c.form.group import Group
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
from zope.interface import implementer_only
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.schema.interfaces import IBytes
from zope.size import byteDisplay

import six
import uuid
import urllib


def _make_namedfile(value, field, widget):
    """Return a NamedImage or NamedFile instance, if it isn't already one -
    e.g. when it's base64 encoded data.
    """

    if INamed.providedBy(value):
        return value

    string_types = (bytes, str)
    if isinstance(value, string_types) and IBytes.providedBy(field):
        filename, data = b64decode_file(value)
    elif isinstance(value, dict) or isinstance(value, PersistentDict):
        filename = value["filename"]
        data = value["data"]

    if INamedBlobImageField.providedBy(field):
        value = NamedBlobImage(data=data, filename=filename)
    elif INamedImageField.providedBy(field):
        value = NamedImage(data=data, filename=filename)
    elif INamedBlobFileField.providedBy(field):
        value = NamedBlobFile(data=data, filename=filename)
    else:
        value = NamedFile(data=data, filename=filename)

    return value


@implementer_only(INamedFileWidget)
class NamedFileWidget(Explicit, FileWidget):
    """A widget for a named file object"""

    klass = "named-file-widget"
    value = None  # don't default to a string
    _file_upload_id = None

    @property
    def is_uploaded(self):
        return utils.is_file_upload(self.value) or INamed.providedBy(self.value)

    @property
    def file_upload_id(self):
        """Temporary store the uploaded file contents with a file_upload_id key.
        In case of form validation errors the already uploaded image can then
        be reused.

        This is only useful on a POST request:
        forms should not be using GET,
        especially when you save something to the database.

        Note that if we want this on a GET request,
        we should add a safeWrite call in the code below:
        plone.protect.utils.safeWrite(up.upload_map, self.request)
        Otherwise plone.protect auto csrf will complain for example
        when getting @@site-controlpanel or @@personal-information
        See https://github.com/plone/Products.CMFPlone/issues/2628
        and https://github.com/plone/Products.CMFPlone/issues/2709
        """
        if self.request.method != "POST":
            return ""
        if self._file_upload_id:
            # cache this property for multiple calls within one request.
            # This avoids storing a file upload multiple times.
            return self._file_upload_id

        upload_id = None
        if self.is_uploaded:
            data = None
            if INamed.providedBy(self.value):
                # previously uploaded and failed
                data = self.value.data
            else:
                self.value.seek(0)
                data = self.value.read()

            upload_id = uuid.uuid4().hex
            up = IFileUploadTemporaryStorage(getSite())
            up.cleanup()
            up.upload_map[upload_id] = PersistentDict(
                filename=self.value.filename,
                data=data,
                dt=datetime.now(),
            )

        self._file_upload_id = upload_id
        return upload_id

    @property
    def allow_nochange(self):
        return (
            self.field is not None
            and self.value is not None
            and self.value != self.field.missing_value
        )

    @property
    def filename(self):
        if INamed.providedBy(self.value):
            return self.value.filename
        elif utils.is_file_upload(self.value):
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
        registry = getToolByName(self.context, "mimetypes_registry", None)
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
            return getattr(self.value, "contentType", None)

    @property
    def file_icon(self):
        if not self.value:
            return None

        mimetype = self._mimetype
        if mimetype and mimetype.icon_path:
            return "{}/{}".format(
                getToolByName(getSite(), "portal_url")(), mimetype.icon_path
            )
        else:
            return None

    @property
    def filename_encoded(self):
        filename = self.filename
        if filename is None:
            return None
        else:
            if isinstance(filename, str):
                filename = filename.encode("utf-8")
            return urllib.parse.quote_plus(filename)

    @property
    def download_url(self):
        if (self.field is None) or self.ignoreContext:
            return None

        url_parts = []

        absolute_url_method = getattr(self.context, "absolute_url", None)
        if absolute_url_method:
            if isinstance(self.form, Group):
                url_parts.extend(
                    [
                        absolute_url_method(),
                        getattr(
                            getattr(self.form, "__parent__", None), "__name__", None
                        ),
                    ]
                )
            else:
                url_parts.extend(
                    [
                        absolute_url_method(),
                        getattr(self.form, "__name__", None),
                    ]
                )
        else:
            url_parts.append(self.request.getURL())

        url_parts.extend(
            ["++widget++" + self.name, "@@download", self.filename_encoded]
        )

        return "/".join(p for p in url_parts if p)

    def action(self):
        action = self.request.get("%s.action" % self.name, "nochange")
        if self.is_uploaded or (
            hasattr(self.form, "successMessage")
            and self.form.status == self.form.successMessage
        ):
            # if form action completed successfully, we want nochange
            action = "nochange"
        return action

    def extract(self, default=NOVALUE):
        url = self.request.getURL()
        action = self.request.get("%s.action" % self.name, None)
        if url.endswith("kss_z3cform_inline_validation") or url.endswith(
            "z3cform_validate_field"
        ):
            # Ignore validation requests.
            action = "nochange"

        if action == "remove":
            return None
        elif action == "nochange":
            if self.value is not None:
                return self.value

            if url.endswith("z3cform_validate_field"):
                # Ignore validation requests.
                return None

            # Handle already uploaded files in case of previous form errors
            file_upload_id = self.request.get("%s.file_upload_id" % self.name) or 0
            if file_upload_id:
                upload_map = IFileUploadTemporaryStorage(getSite()).upload_map
                fileinfo = upload_map.get(file_upload_id, {})
                filename = fileinfo.get("filename")
                data = fileinfo.get("data")

                if filename or data:
                    if filename:
                        filename = safe_basename(filename)
                    if filename is not None and not isinstance(filename, str):
                        # work-around for
                        # https://bugs.launchpad.net/zope2/+bug/499696
                        filename = filename.decode("utf-8")
                    del upload_map[file_upload_id]
                    value = {
                        "data": data,
                        "filename": filename,
                    }
                    ret = _make_namedfile(value, self.field, self)
                    return ret

            if self.ignoreContext:
                return default
            dm = getMultiAdapter(
                (
                    self.context,
                    self.field,
                ),
                IDataManager,
            )
            # For sub-widgets to function use a query() not get()
            data = dm.query(default)
            if data is not None:
                data = _make_namedfile(data, self.field, self.context)
            return data

        # empty unnamed FileUploads should not count as a value
        value = super().extract(default)
        if utils.is_file_upload(value):
            value.seek(0, SEEK_END)
            empty = value.tell() == 0
            value.seek(0)
            if empty and not value.filename:
                return default
            value.seek(0)
        return value


@implementer_only(INamedImageWidget)
class NamedImageWidget(NamedFileWidget):
    """A widget for a named file object"""

    klass = "named-image-widget"

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
        """Return a img tag with a url to the preview scale and the width and
        height of a thumbnail scale.

        This way on high pixel density screens the image is displayed in
        screen pixels.
        On non-high pixel density screens the browser will downsize them
        as used to.
        """
        try:
            scales = getMultiAdapter((self.context, self.request), name="images")
        except ComponentLookupError:
            # For example in the @@site-controlpanel after uploading an image,
            # because the context is a RecordsProxy.
            return ""
        fieldname = self.field.getName()
        thumb_scale = scales.scale(fieldname, scale="thumb")
        preview_scale = scales.scale(fieldname, scale="preview")
        if preview_scale is not None and thumb_scale is not None:
            return preview_scale.tag(width=thumb_scale.width, height=thumb_scale.height)
        return ""

    @property
    def alt(self):
        return self.title


@implementer(IPublishTraverse)
class Download(DownloadBase):
    """Download a file, via ../context/form/++widget++/@@download/filename"""

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
            raise NotFound("Cannot get the data file from a widget with no context")

        if self.context.form is not None:
            content = aq_inner(self.context.form.getContent())
        else:
            content = aq_inner(self.context.context)
        field = aq_inner(self.context.field)

        dm = getMultiAdapter(
            (
                content,
                field,
            ),
            IDataManager,
        )
        file_ = dm.get()
        file_ = _make_namedfile(file_, field, self.context)

        if file_ is None:
            raise NotFound(self, self.filename, self.request)

        if not self.filename:
            self.filename = getattr(file_, "filename", None)

        set_headers(file_, self.request.response, filename=self.filename)
        request_range = self.handle_request_range(file_)
        return stream_data(file_, **request_range)


@implementer(IFieldWidget)
@adapter(INamedFileField, IFormLayer)
def NamedFileFieldWidget(field, request):
    return FieldWidget(field, NamedFileWidget(request))


@implementer(IFieldWidget)
@adapter(INamedImageField, IFormLayer)
def NamedImageFieldWidget(field, request):
    return FieldWidget(field, NamedImageWidget(request))
