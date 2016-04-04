=================
Named File Widget
=================

This package contains two widgets: the NamedFileWidget will be used when
rendering NamedFile objects from plone.namedfile. The NamedImageWidget is used
for NamedImage objects. This includes their sub-classes NamedBlobFile and
NamedBlobImage.

Like any widget, the file widgets provide the ``IWidget`` interface::

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from plone.formwidget.namedfile import NamedFileWidget, NamedImageWidget

  >>> verifyClass(interfaces.IWidget, NamedFileWidget)
  True
  >>> verifyClass(interfaces.IWidget, NamedImageWidget)
  True

There are also more specific interfaces for each widget::

    >>> from plone.formwidget.namedfile.interfaces import INamedFileWidget
    >>> from plone.formwidget.namedfile.interfaces import INamedImageWidget

    >>> verifyClass(INamedFileWidget, NamedFileWidget)
    True
    >>> verifyClass(INamedImageWidget, NamedImageWidget)
    True

The widgets can be instantiated only using the request::

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()

  >>> file_widget = NamedFileWidget(request)
  >>> image_widget = NamedImageWidget(request)

Before rendering a widget, one has to set the name and id of the widget::

  >>> file_widget.id = 'widget.id.file'
  >>> file_widget.name = 'widget.name.file'

  >>> image_widget.id = 'widget.id.image'
  >>> image_widget.name = 'widget.name.image'

We also need to register the templates for the widgets::

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> def getPath(filename):
  ...     import os.path
  ...     import plone.formwidget.namedfile
  ...     return os.path.join(os.path.dirname(plone.formwidget.namedfile.__file__), filename)

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('file_input.pt'), 'text/html'),
  ...     (None, None, None, None, INamedFileWidget),
  ...     IPageTemplate, name=interfaces.INPUT_MODE)

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('image_input.pt'), 'text/html'),
  ...     (None, None, None, None, INamedImageWidget),
  ...     IPageTemplate, name=interfaces.INPUT_MODE)

If we render the widget as this we get an input element in a simple wrapper.
Later, we will show more advanced functionality when using a field-widget::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <span id="widget.id.file" class="named-file-widget">
    <input type="file" id="widget.id.file-input"
           name="widget.name.file" />
  </span>

  >>> image_widget.update()
  >>> print(image_widget.render())
  <span id="widget.id.image" class="named-image-widget">
      <input type="file" id="widget.id.image-input"
             name="widget.name.image" />
  </span>

We can extract simple file data from the widget like this::

  >>> import cStringIO
  >>> myfile = cStringIO.StringIO('My file contents.')

  >>> file_widget.request = TestRequest(form={'widget.name.file': myfile})
  >>> file_widget.update()
  >>> file_widget.extract()
  <cStringIO.StringI object at ...>

  >>> image_widget.request = TestRequest(form={'widget.name.image': myfile})
  >>> image_widget.update()
  >>> image_widget.extract()
  <cStringIO.StringI object at ...>

If nothing is found in the request, the default is returned::

  >>> file_widget.request = TestRequest()
  >>> file_widget.update()
  >>> file_widget.extract()
  <NO_VALUE>

  >>> image_widget.request = TestRequest()
  >>> image_widget.update()
  >>> image_widget.extract()
  <NO_VALUE>

We can also handle file-upload objects::

  >>> import cStringIO
  >>> from ZPublisher.HTTPRequest import FileUpload

Let's define a FieldStorage stub for easy use with the FileUpload::

  >>> class FieldStorageStub:
  ...     def __init__(self, file, headers={}, filename='foo.bar'):
  ...         self.file = file
  ...         self.headers = headers
  ...         self.filename = filename

Now build a FileUpload::

  >>> myfile = cStringIO.StringIO('File upload contents.')
  >>> aFieldStorage = FieldStorageStub(myfile)
  >>> myUpload = FileUpload(aFieldStorage)

  >>> file_widget.request = TestRequest(form={'widget.name.file': myUpload})
  >>> file_widget.update()
  >>> file_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload instance at ...>

  >>> image_widget.request = TestRequest(form={'widget.name.image': myUpload})
  >>> image_widget.update()
  >>> image_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload instance at ...>

The rendering is unchanged::

  >>> print(file_widget.render())
  <span id="widget.id.file" class="named-file-widget">
      <input type="file" id="widget.id.file-input"
             name="widget.name.file" />
  </span>

  >>> print(image_widget.render())
  <span id="widget.id.image" class="named-image-widget">
      <input type="file" id="widget.id.image-input"
             name="widget.name.image" />
  </span>

Empty, unnamed FileUploads are treated as having no value::

  >>> emptyfile = cStringIO.StringIO('')
  >>> aFieldStorage = FieldStorageStub(emptyfile, filename='')
  >>> myEmptyUpload = FileUpload(aFieldStorage)

  >>> file_widget.request = TestRequest(form={'widget.name.file': myEmptyUpload})
  >>> file_widget.update()
  >>> file_widget.extract()
  <NO_VALUE>

  >>> image_widget.request = TestRequest(form={'widget.name.image': myEmptyUpload})
  >>> image_widget.update()
  >>> image_widget.extract()
  <NO_VALUE>


Rendering field widgets
-----------------------

If the widgets are used as field widgets for the fields in plone.namedfile,
we get more interesting behaviour: the user may either select to provide a
new file, or keep the existing one.

For this to work, we need a context and a data manager::

  >>> from DateTime import DateTime
  >>> from plone.namedfile import field
  >>> from zope.interface import implements, Interface
  >>> from plone.namedfile.interfaces import IImageScaleTraversable
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> class IContent(Interface):
  ...     file_field = field.NamedFile(title=u"File")
  ...     image_field = field.NamedImage(title=u"Image")

  >>> class Content(object):
  ...     implements(IContent, IImageScaleTraversable, IAttributeAnnotatable)
  ...     def __init__(self, file, image):
  ...         self.file_field = file
  ...         self.image_field = image
  ...         # modification time is needed for a check in scaling:
  ...         self._p_mtime = DateTime()
  ...
  ...     def absolute_url(self):
  ...         return 'http://example.com/content1'
  ...
  ...     def Title(self):
  ...         return 'A content item'

  >>> content = Content(None, None)

  >>> from z3c.form.datamanager import AttributeField
  >>> from zope.component import provideAdapter
  >>> provideAdapter(AttributeField)

  >>> from plone.formwidget.namedfile import NamedFileFieldWidget
  >>> from plone.formwidget.namedfile import NamedImageFieldWidget

  >>> file_widget = NamedFileFieldWidget(IContent['file_field'], TestRequest())
  >>> image_widget = NamedImageFieldWidget(IContent['image_field'], TestRequest())

  >>> file_widget.context = content
  >>> image_widget.context = content

  >>> file_widget.id = 'widget.id.file'
  >>> file_widget.name = 'widget.name.file'

  >>> image_widget.id = 'widget.id.image'
  >>> image_widget.name = 'widget.name.image'

At first, there is no value, so the behaviour is much like before::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <span id="widget.id.file" class="named-file-widget required namedfile-field">
      <input type="file" id="widget.id.file-input"
             name="widget.name.file" />
  </span>

  >>> image_widget.update()
  >>> print(image_widget.render())
  <span id="widget.id.image" class="named-image-widget required namedimage-field">
      <input type="file" id="widget.id.image-input"
             name="widget.name.image" />
  </span>

However, if we now set a value, we will have the option of keeping it,
or changing it.  The filename can handle unicode and international
characters::

  >>> from plone.namedfile import NamedFile, NamedImage
  >>> from plone.formwidget.namedfile.testing import get_file
  >>> image_data = get_file('image.jpg').read()
  >>> file_widget.value = NamedFile(data='My file data',
  ...                               filename=unicode('data_深.txt', 'utf-8'))
  >>> aFieldStorage = FieldStorageStub(get_file('image.jpg'), filename='faux.jpg')
  >>> myUpload = FileUpload(aFieldStorage)
  >>> image_widget.request = TestRequest(form={'widget.name.image': myUpload})
  >>> file_widget.update()
  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required namedfile-field">...
  <a href="http://127.0.0.1/++widget++widget.name.file/@@download/data_%E6%B7%B1.txt" >data_深.txt</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> image_widget.update()
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required namedimage-field">...
  <a href="http://127.0.0.1/++widget++widget.name.image/@@download/faux.jpg" >faux.jpg</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...

Note: since we did not save anything, no scale is shown.

Notice how there are radio buttons to decide whether to upload a new file or
keep the existing one. If the '.action' field is not submitted or is
empty, the behaviour is the same as before::

  >>> myfile = cStringIO.StringIO('File upload contents.')
  >>> aFieldStorage = FieldStorageStub(myfile, filename='test2.txt')
  >>> myUpload = FileUpload(aFieldStorage)

  >>> file_widget.request = TestRequest(form={'widget.name.file': myUpload})
  >>> file_widget.update()
  >>> file_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload instance at ...>

Set the current image, which is shown as thumb on the page, and then
setup the widget with a new value::

  >>> content.image_field = NamedImage(data=image_data, filename=u'faux.jpg')
  >>> aFieldStorage = FieldStorageStub(get_file('image.jpg'), filename='faux2.jpg')
  >>> myUpload = FileUpload(aFieldStorage)
  >>> image_widget.request = TestRequest(form={'widget.name.image': myUpload})
  >>> image_widget.update()
  >>> image_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload instance at ...>

If the widgets are rendered again, the newly uploaded files will be shown::

  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required namedfile-field">...
  <a href="http://127.0.0.1/++widget++widget.name.file/@@download/test2.txt" >test2.txt</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> print(image_widget.thumb_tag)
  <img src="http://example.com/content1/@@images/...jpeg" alt="A content item" title="A content item" height="51" width="128" />
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required namedimage-field">...
  <img src="http://example.com/content1/@@images/...jpeg" alt="A content item" title="A content item" height="51" width="128" />...
  <a href="http://127.0.0.1/++widget++widget.name.image/@@download/faux2.jpg" >faux2.jpg</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...

However, if we provide the '.action' field, we get back the value currently
stored in the field::

  >>> content.file_field = NamedFile(data='My file data', filename=u'data.txt')
  >>> content.image_field = NamedImage(data=image_data, filename=u'faux.jpg')

  >>> file_widget.value = content.file_field
  >>> image_widget.value = content.image_field

  >>> file_widget.request = TestRequest(form={'widget.name.file': '', 'widget.name.file.action': 'nochange'})
  >>> file_widget.update()
  >>> file_widget.extract() is content.file_field
  True

  >>> aFieldStorage = FieldStorageStub(get_file('image.jpg'), filename='faux2.jpg')
  >>> myUpload = FileUpload(aFieldStorage)

  >>> image_widget.request = TestRequest(form={'widget.name.image': '', 'widget.name.image.action': 'nochange'})
  >>> image_widget.update()
  >>> image_widget.extract() is content.image_field
  True


Download view
-------------

The download view extracts the image/file data, the widget template output uses
this view to display the image itself or link to the file::

  >>> from plone.formwidget.namedfile.widget import Download
  >>> request = TestRequest()
  >>> view = Download(image_widget, request)
  >>> view() == image_data
  True
  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''faux.jpg"

  >>> request = TestRequest()
  >>> view = Download(file_widget, request)
  >>> view()
  'My file data'
  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''data.txt"

The URL will influence the name of the file as reported to the browser, but
doesn't stop it being found::

  >>> request = TestRequest()
  >>> view = Download(file_widget, request)
  >>> view = view.publishTraverse(request, 'daisy.txt')
  >>> view()
  'My file data'
  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''daisy.txt"

Any additional traversal will result in an error::

  >>> request = TestRequest()
  >>> view = Download(file_widget, request)
  >>> view = view.publishTraverse(request, 'cows')
  >>> view = view.publishTraverse(request, 'daisy.txt')
  Traceback (most recent call last):
  ...
  NotFound: ... 'daisy.txt'


The converter
-------------

This package comes with a data converter that can convert a file upload
instance to a named file. It is registered to work on all named file/image
instances and the two named file/image widgets::

  >>> from plone.formwidget.namedfile.converter import NamedDataConverter
  >>> provideAdapter(NamedDataConverter)

  >>> from zope.component import getMultiAdapter
  >>> from z3c.form.interfaces import IDataConverter

  >>> file_converter = getMultiAdapter((IContent['file_field'], file_widget), IDataConverter)
  >>> image_converter = getMultiAdapter((IContent['image_field'], image_widget), IDataConverter)

A value of None or '' results in the field's missing_value being returned::

  >>> file_converter.toFieldValue(u'') is IContent['file_field'].missing_value
  True
  >>> file_converter.toFieldValue(None) is IContent['file_field'].missing_value
  True

  >>> image_converter.toFieldValue(u'') is IContent['image_field'].missing_value
  True
  >>> image_converter.toFieldValue(None) is IContent['image_field'].missing_value
  True

A named file/image instance is returned as-is::

  >>> file_converter.toFieldValue(content.file_field) is content.file_field
  True
  >>> image_converter.toFieldValue(content.image_field) is content.image_field
  True

A data string is converted to the appropriate type::

  >>> file_converter.toFieldValue('some file content')
  <plone.namedfile.file.NamedFile object at ...>

  >>> image_converter.toFieldValue('random data')
  <plone.namedfile.file.NamedImage object at ...>

A FileUpload object is converted to the appropriate type, preserving filename,
and possibly handling international characters in filenames.
The content type sent by the browser will be ignored because it's unreliable
- it's left to the implementation of the file field to determine the proper
content type::

  >>> myfile = cStringIO.StringIO('File upload contents.')
  >>> # \xc3\xb8 is UTF-8 for a small letter o with slash
  >>> aFieldStorage = FieldStorageStub(myfile, filename='rand\xc3\xb8m.txt',
  ...     headers={'Content-Type': 'text/x-dummy'})
  >>> file_obj = file_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> file_obj.data
  'File upload contents.'
  >>> file_obj.filename
  u'rand\xf8m.txt'

Content type from headers sent by browser should be ignored::

  >>> file_obj.contentType != 'text/x-dummy'
  True

  >>> aFieldStorage = FieldStorageStub(get_file('image.jpg'), filename='random.png', headers={'Content-Type': 'image/x-dummy'})
  >>> image_obj = image_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> image_obj.data == image_data
  True
  >>> image_obj.filename
  u'random.png'
  >>> image_obj.contentType != 'image/x-dummy'
  True


However, a zero-length, unnamed FileUpload results in the field's missing_value
being returned::

  >>> myfile = cStringIO.StringIO('')
  >>> aFieldStorage = FieldStorageStub(myfile, filename='', headers={'Content-Type': 'application/octet-stream'})
  >>> field_value = file_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> field_value is IContent['file_field'].missing_value
  True
  >>> field_value = image_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> field_value is IContent['image_field'].missing_value
  True


The Base64Converter for ASCII fields
------------------------------------

There is another converter, which converts between a NamedFile or file upload
instance and base64 encoded data, which can be stored in a ASCII field::

  >>> from zope import schema
  >>> from zope.interface import implements, Interface
  >>> class IASCIIContent(Interface):
  ...     file_field = schema.ASCII(title=u"File")
  ...     image_field = schema.ASCII(title=u"Image")

  >>> from plone.formwidget.namedfile.converter import Base64Converter
  >>> provideAdapter(Base64Converter)

  >>> from zope.component import getMultiAdapter
  >>> from z3c.form.interfaces import IDataConverter

  >>> ascii_file_converter = getMultiAdapter(
  ...     (IASCIIContent['file_field'], file_widget),
  ...     IDataConverter
  ... )
  >>> ascii_image_converter = getMultiAdapter(
  ...     (IASCIIContent['image_field'], image_widget),
  ...     IDataConverter
  ... )

A value of None or '' results in the field's missing_value being returned::

  >>> ascii_file_converter.toFieldValue(u'') is IASCIIContent['file_field'].missing_value
  True
  >>> ascii_file_converter.toFieldValue(None) is IASCIIContent['file_field'].missing_value
  True

  >>> ascii_image_converter.toFieldValue(u'') is IASCIIContent['image_field'].missing_value
  True
  >>> ascii_image_converter.toFieldValue(None) is IASCIIContent['image_field'].missing_value
  True

A named file/image instance is returned as Base 64 encoded string in the
following form::

  filenameb64:BASE64_ENCODED_FILENAME;data64:BASE64_ENCODED_DATA

Like so::

  >>> ascii_file_converter.toFieldValue(
  ...     NamedFile(data='testfile', filename=u'test.txt'))
  'filenameb64:dGVzdC50eHQ=;datab64:dGVzdGZpbGU='
  >>> ascii_image_converter.toFieldValue(
  ...     NamedImage(data='testimage', filename=u'test.png'))
  'filenameb64:dGVzdC5wbmc=;datab64:dGVzdGltYWdl'

A Base 64 encoded structure like descibed above is converted to the appropriate
type::

  >>> afile = ascii_file_converter.toWidgetValue(
  ...     'filenameb64:dGVzdC50eHQ=;datab64:dGVzdGZpbGU=')
  >>> afile
  <plone.namedfile.file.NamedFile object at ...>
  >>> afile.data
  'testfile'
  >>> afile.filename
  u'test.txt'

  >>> aimage = ascii_image_converter.toWidgetValue(
  ...     'filenameb64:dGVzdC5wbmc=;datab64:dGVzdGltYWdl')
  >>> aimage
  <plone.namedfile.file.NamedImage object at ...>
  >>> aimage.data
  'testimage'
  >>> aimage.filename
  u'test.png'

Finally, some tests with image uploads converted to the field value.

Convert a file upload to the Base 64 encoded field value and handle the
filename too::


  >>> myfile = cStringIO.StringIO('File upload contents.')
  >>> # \xc3\xb8 is UTF-8 for a small letter o with slash
  >>> aFieldStorage = FieldStorageStub(myfile, filename='rand\xc3\xb8m.txt',
  ...     headers={'Content-Type': 'text/x-dummy'})
  >>> ascii_file_converter.toFieldValue(FileUpload(aFieldStorage))
  'filenameb64:cmFuZMO4bS50eHQ=;datab64:RmlsZSB1cGxvYWQgY29udGVudHMu'

A zero-length, unnamed FileUpload results in the field's missing_value
being returned::

  >>> myfile = cStringIO.StringIO('')
  >>> aFieldStorage = FieldStorageStub(myfile, filename='', headers={'Content-Type': 'application/octet-stream'})
  >>> field_value = ascii_file_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> field_value is IASCIIContent['file_field'].missing_value
  True
  >>> field_value = ascii_image_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> field_value is IASCIIContent['image_field'].missing_value
  True


Rendering ASCII field widgets
-----------------------------

The widgets let the user to upload file and image data and select, if previous data should be kept, deleted or overwritten.

First, let's do the setup::

  >>> class ASCIIContent(object):
  ...     implements(IASCIIContent, IImageScaleTraversable, IAttributeAnnotatable)
  ...     def __init__(self, file, image):
  ...         self.file_field = file
  ...         self.image_field = image
  ...         # modification time is needed for a check in scaling:
  ...         self._p_mtime = DateTime()
  ...
  ...     def absolute_url(self):
  ...         return 'http://example.com/content1'
  ...
  ...     def Title(self):
  ...         return 'A content item'

  >>> content = ASCIIContent(None, None)

  >>> from z3c.form.datamanager import AttributeField
  >>> from zope.component import provideAdapter
  >>> provideAdapter(AttributeField)

  >>> from plone.formwidget.namedfile import NamedFileFieldWidget
  >>> from plone.formwidget.namedfile import NamedImageFieldWidget

  >>> def setup_widget(widget_type, context, set_widget_value=False):
  ...     if widget_type == 'image':
  ...         widget = NamedImageFieldWidget
  ...     else:
  ...         widget = NamedFileFieldWidget
  ...     widget = widget(
  ...         IASCIIContent['{0}_field'.format(widget_type)],
  ...         TestRequest()
  ...     )
  ...     widget.context = context
  ...     widget.id = 'widget.id.{0}'.format(widget_type)
  ...     widget.name = 'widget.name.{0}'.format(widget_type)
  ...
  ...     if set_widget_value:
  ...         converter = globals()['ascii_{0}_converter'.format(widget_type)]
  ...         value = getattr(context, '{0}_field'.format(widget_type))
  ...         widget.value = converter.toWidgetValue(value)
  ...
  ...     return widget

  >>> file_widget = setup_widget('file', content, True)
  >>> image_widget = setup_widget('image', content)


Our content has no value yet::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <span id="widget.id.file" class="named-file-widget required ascii-field">
      <input type="file" id="widget.id.file-input" name="widget.name.file" />
  </span>

  >>> image_widget.update()
  >>> print(image_widget.render())
  <span id="widget.id.image" class="named-image-widget required ascii-field">
      <input type="file" id="widget.id.image-input" name="widget.name.image" />
  </span>


Let's upload data::

  >>> data = cStringIO.StringIO('file 1 content.')
  >>> field_storage = FieldStorageStub(data, filename='file1.txt')
  >>> upload = FileUpload(field_storage)

  >>> file_widget.request = TestRequest(form={'widget.name.file': upload})
  >>> file_widget.update()
  >>> uploaded = file_widget.extract()
  >>> uploaded
  <ZPublisher.HTTPRequest.FileUpload instance at ...>

  >>> content.file_field = ascii_file_converter.toFieldValue(uploaded)
  >>> content.file_field
  'filenameb64:ZmlsZTEudHh0;datab64:ZmlsZSAxIGNvbnRlbnQu'

Check that we have a good image that PIL can handle:

  >>> import PIL.Image
  >>> PIL.Image.open(get_file('image.jpg'))
  <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=500x200 at ...>
  >>> field_storage = FieldStorageStub(get_file('image.jpg'), filename='image.jpg')
  >>> upload = FileUpload(field_storage)

  >>> image_widget.request = TestRequest(form={'widget.name.image': upload})
  >>> image_widget.update()
  >>> uploaded = image_widget.extract()
  >>> uploaded
  <ZPublisher.HTTPRequest.FileUpload instance at ...>

  >>> content.image_field = ascii_image_converter.toFieldValue(uploaded)
  >>> print(content.image_field)
  filenameb64:aW1hZ2UuanBn;datab64:/9j/4AAQSkZJRgABAQEAYABgAAD/...

Note that PIL cannot open this ascii image, so we cannot scale it::

  >>> PIL.Image.open(cStringIO.StringIO(content.image_field))
  Traceback (most recent call last):
  ...
  IOError: cannot identify image file <cStringIO.StringI object at ...>

Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content, True)
  >>> image_widget = setup_widget('image', content, True)


The upload shows up in the rendered widget::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required ascii-field">...
  <a href="http://127.0.0.1/++widget++widget.name.file/@@download/file1.txt" >file1.txt</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> image_widget.update()
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required ascii-field">...
  <a href="http://127.0.0.1/++widget++widget.name.image/@@download/image.jpg" >image.jpg</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...

Like we said, we cannot scale this ascii image, so the thumb tag is empty::

  >>> print(image_widget.thumb_tag)

Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content)
  >>> image_widget = setup_widget('image', content)


Now overwrite with other data::

  >>> data = cStringIO.StringIO('random file content')
  >>> field_storage = FieldStorageStub(data, filename='plone.pdf')
  >>> upload = FileUpload(field_storage)

  >>> file_widget.request = TestRequest(form={'widget.name.file': upload, 'widget.name.file.action': 'replace'})
  >>> file_widget.update()
  >>> uploaded = file_widget.extract()
  >>> uploaded
  <ZPublisher.HTTPRequest.FileUpload instance at ...>

  >>> content.file_field = ascii_file_converter.toFieldValue(uploaded)
  >>> content.file_field
  'filenameb64:cGxvbmUucGRm;datab64:cmFuZG9tIGZpbGUgY29udGVudA=='


  >>> data = cStringIO.StringIO('no image')
  >>> field_storage = FieldStorageStub(data, filename='logo.tiff')
  >>> upload = FileUpload(field_storage)

  >>> image_widget.request = TestRequest(form={'widget.name.image': upload, 'widget.name.image.action': 'replace'})
  >>> image_widget.update()
  >>> uploaded = image_widget.extract()
  >>> uploaded
  <ZPublisher.HTTPRequest.FileUpload instance at ...>

  >>> content.image_field = ascii_file_converter.toFieldValue(uploaded)
  >>> content.image_field
  'filenameb64:bG9nby50aWZm;datab64:bm8gaW1hZ2U='


Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content, True)
  >>> image_widget = setup_widget('image', content, True)


The new image/file shows up in the rendered widget::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required ascii-field">...
  <a href="http://127.0.0.1/++widget++widget.name.file/@@download/plone.pdf" >plone.pdf</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> image_widget.update()
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required ascii-field">...
  <a href="http://127.0.0.1/++widget++widget.name.image/@@download/logo.tiff" >logo.tiff</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...


Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content)
  >>> image_widget = setup_widget('image', content)

#  >>> interact(locals())

Resubmit, but keep the data::

  >>> file_widget.request = TestRequest(form={'widget.name.file': '', 'widget.name.file.action': 'nochange'})
  >>> file_widget.update()
  >>> uploaded = file_widget.extract()
  >>> uploaded
  <plone.namedfile.file.NamedFile object at ...>

  >>> content.file_field = ascii_file_converter.toFieldValue(uploaded)
  >>> content.file_field
  'filenameb64:cGxvbmUucGRm;datab64:cmFuZG9tIGZpbGUgY29udGVudA=='


  >>> image_widget.request = TestRequest(form={'widget.name.image': '', 'widget.name.image.action': 'nochange'})
  >>> image_widget.update()
  >>> uploaded = image_widget.extract()
  >>> uploaded
  <plone.namedfile.file.NamedFile object at ...>

  >>> content.image_field = ascii_file_converter.toFieldValue(uploaded)
  >>> content.image_field
  'filenameb64:bG9nby50aWZm;datab64:bm8gaW1hZ2U='


Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content, True)
  >>> image_widget = setup_widget('image', content, True)


The previous image/file should be kept::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required ascii-field">...
  <a href="http://127.0.0.1/++widget++widget.name.file/@@download/plone.pdf" >plone.pdf</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> image_widget.update()
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required ascii-field">...
  <a href="http://127.0.0.1/++widget++widget.name.image/@@download/logo.tiff" >logo.tiff</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...


The Download view on ASCII fields
---------------------------------
::

  >>> class ASCIIContent(object):
  ...     implements(IASCIIContent)
  ...     def __init__(self, file, image):
  ...         self.file_field = file
  ...         self.image_field = image
  ...
  ...     def absolute_url(self):
  ...         return 'http://example.com/content2'

  >>> content = ASCIIContent(
  ...     NamedFile(data="testfile", filename=u"test.txt"),
  ...     NamedImage(data="testimage", filename=u"test.jpg"))

  >>> from z3c.form.widget import FieldWidget

  >>> ascii_file_widget = FieldWidget(IASCIIContent['file_field'], NamedFileWidget(TestRequest()))
  >>> ascii_file_widget.context = content

  >>> ascii_image_widget = FieldWidget(IASCIIContent['image_field'], NamedImageWidget(TestRequest()))
  >>> ascii_image_widget.context = content

  >>> request = TestRequest()
  >>> view = Download(ascii_file_widget, request)
  >>> view()
  'testfile'

  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''test.txt"

  >>> view = Download(ascii_image_widget, request)
  >>> view()
  'testimage'

  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''test.jpg"


The validator
-------------

If the user clicked 'replace' but did not provide a file, we want to get a
validation error::

  >>> from plone.formwidget.namedfile.validator import NamedFileWidgetValidator

If 'action' is omitted and the value is None, we should get a validation error
only when the field is required::

  >>> request = TestRequest(form={'widget.name.file': myfile})
  >>> validator = NamedFileWidgetValidator(content, request, None, IContent['file_field'], file_widget)
  >>> validator.validate(None) is None
  Traceback (most recent call last):
  ...
  RequiredMissing...
  >>> IContent['file_field'].required = False
  >>> validator.validate(None) is None
  True

However, if it is set to 'replace' and there is no value provided, we get the
InvalidState exception from validator.py (its docstring is displayed to the
user)::

  >>> request = TestRequest(form={'widget.name.file': myfile, 'widget.name.file.action': 'replace'})
  >>> validator = NamedFileWidgetValidator(content, request, None, IContent['file_field'], file_widget)
  >>> validator.validate(None)
  Traceback (most recent call last):
  ...
  InvalidState

If we provide a file, all is good::

  >>> request = TestRequest(form={'widget.name.file': myfile, 'widget.name.file.action': 'replace'})
  >>> validator = NamedFileWidgetValidator(content, request, None, IContent['file_field'], file_widget)
  >>> validator.validate(file_obj) is None
  True

Similarly, if we really wanted to remove the file, we won't complain, unless
we again make the field required::

  >>> request = TestRequest(form={'widget.name.file': myfile, 'widget.name.file.action': 'remove'})
  >>> validator = NamedFileWidgetValidator(content, request, None, IContent['file_field'], file_widget)
  >>> validator.validate(None) is None
  True
  >>> IContent['file_field'].required = True
  >>> validator.validate(None) is None
  Traceback (most recent call last):
  ...
  RequiredMissing...
