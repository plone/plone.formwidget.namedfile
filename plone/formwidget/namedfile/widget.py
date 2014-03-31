#-*- coding: utf-8 -*-

from zope.component import adapter
from zope.interface import implementer, implementsOnly

from z3c.form.widget import FieldWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer

from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
from plone.namedfile.interfaces import INamedImage

from plone.formwidget.namedfile.interfaces import INamedFileWidget
from plone.formwidget.namedfile.interfaces import INamedImageWidget
from plone.formwidget.namedfile.base import BaseNamedFileWidget

from plone.app.widgets.base import InputWidget
from plone.app.widgets.dx import BaseWidget


class NamedFileWidget(BaseWidget, BaseNamedFileWidget):
    """A widget for a named file object
    """
    implementsOnly(INamedFileWidget)

    klass = u'named-file-widget pat-upload'
    value = None  # don't default to a string

    _base = InputWidget

    pattern = 'upload'
    pattern_options = BaseWidget.pattern_options.copy()

    def _base_args(self):
        args = super(NamedFileWidget, self)._base_args()
        # update input element type
        args['type'] = 'file'
        return args

    def render(self):
        print __file__
        print 'WTF HERE I AM!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        return super(NamedFileWidget, self).render()


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


@implementer(IFieldWidget)
@adapter(INamedFileField, IFormLayer)
def NamedFileFieldWidget(field, request):
    return FieldWidget(field, NamedFileWidget(request))


@implementer(IFieldWidget)
@adapter(INamedImageField, IFormLayer)
def NamedImageFieldWidget(field, request):
    return FieldWidget(field, NamedImageWidget(request))
