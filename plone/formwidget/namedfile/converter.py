# -*- coding: utf-8 -*-
from plone.formwidget.namedfile.interfaces import INamedFileWidget
from plone.formwidget.namedfile.interfaces import INamedImageWidget
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import INamed
from plone.namedfile.interfaces import INamedField
from plone.namedfile.utils import safe_basename
from z3c.form.converter import BaseDataConverter
from zope.component import adapts
from zope.schema.interfaces import IASCII
from ZPublisher.HTTPRequest import FileUpload
import base64


class NamedDataConverter(BaseDataConverter):
    """Converts from a file-upload to a NamedFile variant.
    """
    adapts(INamedField, INamedFileWidget)

    def toWidgetValue(self, value):
        return value

    def toFieldValue(self, value):

        if value is None or value == '':
            return self.field.missing_value

        if INamed.providedBy(value):
            return value
        elif isinstance(value, FileUpload):

            filename = safe_basename(value.filename)

            if filename is not None and not isinstance(filename, unicode):
                # Work-around for
                # https://bugs.launchpad.net/zope2/+bug/499696
                filename = filename.decode('utf-8')

            value.seek(0)
            data = value.read()
            if data or filename:
                return self.field._type(data=data, filename=filename)
            else:
                return self.field.missing_value

        else:
            return self.field._type(data=str(value))


def b64encode_file(filename, data):
    # encode filename and data using the standard alphabet, so that ";" can be
    # used as delimiter.
    if isinstance(filename, unicode):
        filename = filename.encode('utf-8')
    filenameb64 = base64.standard_b64encode(filename or '')
    datab64 = base64.standard_b64encode(data)
    filename = "filenameb64:%s;datab64:%s" % (
        filenameb64, datab64
    )
    return filename.encode('ascii')


def b64decode_file(value):
    filename, data = value.split(';')

    filename = filename.split(':')[1]
    filename = base64.standard_b64decode(filename)
    filename = filename.decode('utf-8')

    data = data.split(':')[1]
    data = base64.standard_b64decode(data)

    return filename, data


class Base64Converter(BaseDataConverter):
    """Converts between ASCII fields with base64 encoded data and a filename
    and INamedImage/INamedFile values.
    """
    adapts(IASCII, INamedFileWidget)

    def toWidgetValue(self, value):

        if not isinstance(value, basestring):
            return None

        filename, data = b64decode_file(value)

        if INamedImageWidget.providedBy(self.widget):
            value = NamedImage(data=data, filename=filename)
        else:
            value = NamedFile(data=data, filename=filename)
        return value

    def toFieldValue(self, value):

        filename = None
        data = None

        if INamed.providedBy(value):
            filename = value.filename
            data = value.data

        elif isinstance(value, FileUpload):
            filename = safe_basename(value.filename)
            value.seek(0)
            data = value.read()

        if not data:
            return self.field.missing_value

        return b64encode_file(filename, data)
