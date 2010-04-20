try:
    from  os import SEEK_END
except ImportError:
    from posixfile import SEEK_END
import urllib

from zope.component import adapter, getMultiAdapter
from zope.interface import implementer, implements, implementsOnly

from z3c.form.interfaces import IFieldWidget, IFormLayer, IDataManager, NOVALUE
from z3c.form.widget import FieldWidget
from z3c.form.browser import file

from plone.namedfile.interfaces import INamedFileField, INamedImageField, INamed, INamedImage
from plone.namedfile.utils import safe_basename, set_headers, stream_data

from plone.formwidget.namedfile.interfaces import INamedFileWidget, INamedImageWidget

from Products.Five.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse, NotFound

from Acquisition import Explicit, aq_inner

from ZPublisher.HTTPRequest import FileUpload

class NamedFileWidget(Explicit, file.FileWidget):
    """A widget for a named file object
    """
    implementsOnly(INamedFileWidget)

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

    @property
    def download_url(self):
        if self.field is None:
            return None
        if self.ignoreContext:
            return None
        if self.filename_encoded:
            return "%s/++widget++%s/@@download/%s" % (self.request.getURL(), self.field.__name__, self.filename_encoded)
        else:
            return "%s/++widget++%s/@@download" % (self.request.getURL(), self.field.__name__)
    
    def action(self):
        return self.request.get("%s.action" % self.name, "nochange")
    
    def extract(self, default=NOVALUE):
        action = self.request.get("%s.action" % self.name, None)
        if action == 'remove':
            return None
        elif action == 'nochange':
            if self.form.ignoreContext:
                return default
            dm = getMultiAdapter((self.context, self.field,), IDataManager)
            return dm.get()

        # empty unnamed FileUploads should not count as a value
        value = super(NamedFileWidget, self).extract(default)
        if isinstance(value, FileUpload):
            value.seek(0, SEEK_END)
            empty = value.tell()==0
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
    def thumb_width(self):
        width = self.width
        if not width:
            return 128
        else:
            return min(width, 128)

    @property
    def thumb_height(self):
        height = self.height
        if not height:
            return 128
        else:
            return min(height, 128)

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
        
        if self.filename is None: # ../@@download/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)
        
        return self
    
    def __call__(self):
        
        # TODO: Security check on form view/widget
        
        if self.context.ignoreContext:
            raise NotFound("Cannot get the data file from a widget with no context")
        
        context = aq_inner(self.context.context)
        field = aq_inner(self.context.field)
        
        dm = getMultiAdapter((context, field,), IDataManager)
        file_ = dm.get()
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
