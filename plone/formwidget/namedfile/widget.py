import urllib

import zope.component
import zope.interface

from z3c.form.interfaces import IFieldWidget, IFormLayer, IDataManager, NOVALUE
from z3c.form.widget import FieldWidget
from z3c.form.browser import file

from plone.namedfile.interfaces import INamedFileField, INamedImageField, INamed, INamedImage
from plone.namedfile.utils import safe_basename

from plone.formwidget.namedfile.interfaces import INamedFileWidget, INamedImageWidget


from ZPublisher.HTTPRequest import FileUpload

class NamedFileWidget(file.FileWidget):
    """A widget for a named file object
    """
    zope.interface.implementsOnly(INamedFileWidget)

    klass = u'named-file-widget'
    value = None # don't default to a string
    
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
            return self.value.getSize() / 1024
        else:
            return 0
    
    @property
    def filename_encoded(self):
        filename = self.filename
        if filename is None:
            return None
        else:
            return urllib.quote_plus(filename)

    def extract(self, default=NOVALUE):
        nochange = self.request.get("%s.nochange" % self.name, None)
        if nochange == 'nochange':
            dm = zope.component.getMultiAdapter((self.context, self.field,), IDataManager)
            return dm.get()
        else:
            return super(NamedFileWidget, self).extract(default)

class NamedImageWidget(NamedFileWidget):
    """A widget for a named file object
    """
    zope.interface.implementsOnly(INamedImageWidget)

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
            return self.value._width
        else:
            return None

    @property
    def thumb_width(self):
        width = self.width
        if width is None:
            return None
        else:
            return min(width, 48)

    @property
    def thumb_height(self):
        height = self.height
        if height is None:
            return None
        else:
            return min(height, 48)

    @property
    def alt(self):
        return self.title

@zope.interface.implementer(IFieldWidget)
@zope.component.adapter(INamedFileField, IFormLayer)
def NamedFileFieldWidget(field, request):
    return FieldWidget(field, NamedFileWidget(request))

@zope.interface.implementer(IFieldWidget)
@zope.component.adapter(INamedImageField, IFormLayer)
def NamedImageFieldWidget(field, request):
    return FieldWidget(field, NamedImageWidget(request))