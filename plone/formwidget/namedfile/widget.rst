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
  >>> def make_get_request(**kwargs):
  ...     # GET is actually the default.
  ...     # return TestRequest(**kwargs)
  ...     req = TestRequest(**kwargs)
  ...     req.method = 'GET'
  ...     return req
  >>> def make_request(**kwargs):
  ...     req = TestRequest(**kwargs)
  ...     req.method = 'POST'
  ...     return req
  >>> request = make_request()
  >>> def make_file_widget(request):
  ...     file_widget = NamedFileWidget(request)
  ...     # In some versions, before rendering a widget, one has to set the name and id of the widget:
  ...     file_widget.id = 'widget.id.file'
  ...     file_widget.name = 'widget.name.file'
  ...     return file_widget
  >>> def make_image_widget(request):
  ...     image_widget = NamedImageWidget(request)
  ...     # In some versions, before rendering a widget, one has to set the name and id of the widget:
  ...     image_widget.id = 'widget.id.image'
  ...     image_widget.name = 'widget.name.image'
  ...     return image_widget
  >>> file_widget = make_file_widget(request)
  >>> image_widget = make_image_widget(request)

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

  >>> import six
  >>> myfile = six.BytesIO(b'My file contents.')

  >>> file_widget = make_file_widget(make_request(form={'widget.name.file': myfile}))
  >>> file_widget.update()
  >>> file_widget.extract()
  <...IO object at ...>

  >>> image_widget = make_image_widget(make_request(form={'widget.name.image': myfile}))
  >>> image_widget.update()
  >>> image_widget.extract()
  <...IO object at ...>

If nothing is found in the request, the default is returned::

  >>> file_widget = make_file_widget(make_request())
  >>> file_widget.update()
  >>> file_widget.extract()
  <NO_VALUE>

  >>> image_widget = make_image_widget(make_request())
  >>> image_widget.update()
  >>> image_widget.extract()
  <NO_VALUE>

We can also handle file-upload objects::

  >>> from ZPublisher.HTTPRequest import FileUpload

Let's define a FieldStorage stub for easy use with the FileUpload::

  >>> class FieldStorageStub(object):
  ...     def __init__(self, file, headers={}, filename='foo.bar'):
  ...         self.file = file
  ...         self.headers = headers
  ...         self.filename = filename
  ...         self.name = filename

Now build a FileUpload::

  >>> myfile = six.BytesIO(b'File upload contents.')
  >>> aFieldStorage = FieldStorageStub(myfile)
  >>> myUpload = FileUpload(aFieldStorage)

First use a GET request::

  >>> file_widget = make_file_widget(make_get_request(form={'widget.name.file': myUpload}))
  >>> file_widget.update()
  >>> file_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload ...>

  >>> image_widget = make_image_widget(make_get_request(form={'widget.name.image': myUpload}))
  >>> image_widget.update()
  >>> image_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload ...>

The rendering is unchanged:

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

Now use a POST request (the default in our make_request helper function)::

  >>> file_widget = make_file_widget(make_request(form={'widget.name.file': myUpload}))
  >>> file_widget.update()
  >>> file_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload ...>

  >>> image_widget = make_image_widget(make_request(form={'widget.name.image': myUpload}))
  >>> image_widget.update()
  >>> image_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload ...>

The rendering contains data about the file upload id::

  >>> print(file_widget.render())
  <span id="widget.id.file" class="named-file-widget">
      <input type="hidden" name="widget.name.file.file_upload_id" value="...
      <span>
        File already uploaded:
        foo.bar
      </span>
      <input type="file" id="widget.id.file-input"
             name="widget.name.file" />
  </span>

  >>> print(image_widget.render())
  <span id="widget.id.image" class="named-image-widget">
      <input type="hidden" name="widget.name.image.file_upload_id" value="...
      <span>
        Image already uploaded:
        foo.bar
      </span>
      <input type="file" id="widget.id.image-input"
             name="widget.name.image" />
  </span>

Empty, unnamed FileUploads are treated as having no value::

  >>> emptyfile = six.BytesIO(b'')
  >>> aFieldStorage = FieldStorageStub(emptyfile, filename='')
  >>> myEmptyUpload = FileUpload(aFieldStorage)

  >>> file_widget = make_file_widget(make_request(form={'widget.name.file': myEmptyUpload}))
  >>> file_widget.update()
  >>> file_widget.extract()
  <NO_VALUE>

  >>> image_widget = make_image_widget(make_request(form={'widget.name.image': myEmptyUpload}))
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
  >>> from zope.interface import implementer, Interface
  >>> from plone.namedfile.interfaces import IImageScaleTraversable
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> class IContent(Interface):
  ...     file_field = field.NamedFile(title=u"File")
  ...     image_field = field.NamedImage(title=u"Image")

  >>> root_url = TestRequest().getURL()
  >>> @implementer(IContent, IImageScaleTraversable, IAttributeAnnotatable)
  ... class Content(object):
  ...     def __init__(self, file, image):
  ...         self.file_field = file
  ...         self.image_field = image
  ...         # modification time is needed for a check in scaling:
  ...         self._p_mtime = DateTime()
  ...         self.path = '/content1'
  ...
  ...     def absolute_url(self):
  ...         return root_url + self.path
  ...
  ...     def Title(self):
  ...         return 'A content item'

  >>> content = Content(None, None)

  >>> def make_request(path=None, **kwargs):
  ...     path = path or content.path
  ...     return TestRequest(SCRIPT_NAME=path.lstrip('/'), **kwargs)

  >>> from z3c.form.datamanager import AttributeField
  >>> from zope.component import provideAdapter
  >>> provideAdapter(AttributeField)

  >>> from plone.formwidget.namedfile import NamedFileFieldWidget
  >>> from plone.formwidget.namedfile import NamedImageFieldWidget

  >>> file_widget = NamedFileFieldWidget(IContent['file_field'], make_request())
  >>> image_widget = NamedImageFieldWidget(IContent['image_field'], make_request())

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
  >>> open_files = []
  >>> with get_file('image.jpg') as image_file:
  ...     image_data = image_file.read()
  >>> file_widget.value = NamedFile(data=b'My file data',
  ...                               filename=u'data_深.txt')
  >>> open_files.append(get_file('image.jpg'))
  >>> aFieldStorage = FieldStorageStub(open_files[-1], filename='faux.jpg')
  >>> myUpload = FileUpload(aFieldStorage)
  >>> image_widget.request = make_request(form={'widget.name.image': myUpload})
  >>> file_widget.update()
  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required namedfile-field">...
  <a href="http://127.0.0.1/content1/++widget++widget.name.file/@@download/data_%E6%B7%B1.txt" >data_深.txt</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> image_widget.update()
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required namedimage-field">...
  <a href="http://127.0.0.1/content1/++widget++widget.name.image/@@download/faux.jpg" >faux.jpg</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...

Note: since we did not save anything, no scale is shown.

Notice how there are radio buttons to decide whether to upload a new file or
keep the existing one. If the '.action' field is not submitted or is
empty, the behaviour is the same as before::

  >>> myfile = six.BytesIO(b'File upload contents.')
  >>> aFieldStorage = FieldStorageStub(myfile, filename='test2.txt')
  >>> myUpload = FileUpload(aFieldStorage)

  >>> file_widget.request = make_request(form={'widget.name.file': myUpload})
  >>> file_widget.update()
  >>> file_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload ...>

Set the current image, which is shown as thumb on the page, and then
setup the widget with a new value::

  >>> content.image_field = NamedImage(data=image_data, filename=u'faux.jpg')
  >>> open_files.append(get_file('image.jpg'))
  >>> aFieldStorage = FieldStorageStub(open_files[-1], filename='faux2.jpg')
  >>> myUpload = FileUpload(aFieldStorage)
  >>> image_widget.request = make_request(form={'widget.name.image': myUpload})
  >>> image_widget.update()
  >>> image_widget.extract()
  <ZPublisher.HTTPRequest.FileUpload ...>

If the widgets are rendered again, the newly uploaded files will be shown::

  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required namedfile-field">...
  <a href="http://127.0.0.1/content1/++widget++widget.name.file/@@download/test2.txt" >test2.txt</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> print(image_widget.thumb_tag)
  <img src="http://127.0.0.1/content1/@@images/...jpeg" alt="A content item" title="A content item" height="..." width="..." />
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required namedimage-field">...
  <img src="http://127.0.0.1/content1/@@images/...jpeg" alt="A content item" title="A content item" height="..." width="..." />...
  <a href="http://127.0.0.1/content1/++widget++widget.name.image/@@download/faux2.jpg" >faux2.jpg</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...

However, if we provide the '.action' field, we get back the value currently
stored in the field::

  >>> content.file_field = NamedFile(data=b'My file data', filename=u'data.txt')
  >>> content.image_field = NamedImage(data=image_data, filename=u'faux.jpg')

  >>> file_widget.value = content.file_field
  >>> image_widget.value = content.image_field

  >>> file_widget.request = make_request(form={'widget.name.file': '', 'widget.name.file.action': 'nochange'})
  >>> file_widget.update()
  >>> file_widget.extract() is content.file_field
  True

  >>> open_files.append(get_file('image.jpg'))
  >>> aFieldStorage = FieldStorageStub(open_files[-1], filename='faux2.jpg')
  >>> myUpload = FileUpload(aFieldStorage)

  >>> image_widget.request = make_request(form={'widget.name.image': '', 'widget.name.image.action': 'nochange'})
  >>> image_widget.update()
  >>> image_widget.extract() is content.image_field
  True


Download view
-------------

The download view extracts the image/file data, the widget template output uses
this view to display the image itself or link to the file::

  >>> from plone.formwidget.namedfile.widget import Download
  >>> request = make_request()
  >>> view = Download(image_widget, request)
  >>> view() == image_data
  True
  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''faux.jpg"

  >>> request = make_request()
  >>> view = Download(file_widget, request)
  >>> view()
  b'My file data'
  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''data.txt"

The URL will influence the name of the file as reported to the browser, but
doesn't stop it being found::

  >>> request = make_request()
  >>> view = Download(file_widget, request)
  >>> view = view.publishTraverse(request, 'daisy.txt')
  >>> view()
  b'My file data'
  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''daisy.txt"

Any additional traversal will result in an error::

  >>> request = make_request()
  >>> view = Download(file_widget, request)
  >>> view = view.publishTraverse(request, 'cows')
  >>> view = view.publishTraverse(request, 'daisy.txt')
  Traceback (most recent call last):
  ...
  zope.publisher.interfaces.NotFound: ... 'daisy.txt'


The converter
-------------

This package comes with a data converter that can convert a file upload
instance to a named file. It is registered to work on all named file/image
instances and the two named file/image widgets::

  >>> from plone.formwidget.namedfile.converter import NamedDataConverter
  >>> provideAdapter(NamedDataConverter)

  >>> from zope.component import getMultiAdapter
  >>> from z3c.form.interfaces import IDataConverter
  >>> from z3c.form.interfaces import NOT_CHANGED

  >>> file_converter = getMultiAdapter((IContent['file_field'], file_widget), IDataConverter)
  >>> image_converter = getMultiAdapter((IContent['image_field'], image_widget), IDataConverter)

An initial upload of a file will never include the action field,
so let's remove it from our test requests

  >>> del file_widget.request.form['widget.name.file.action']
  >>> del image_widget.request.form['widget.name.image.action']

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

  >>> image_converter.toFieldValue(b'random data')
  <plone.namedfile.file.NamedImage object at ...>

A FileUpload object is converted to the appropriate type, preserving filename,
and possibly handling international characters in filenames.
The content type sent by the browser will be ignored because it's unreliable
- it's left to the implementation of the file field to determine the proper
content type::

  >>> myfile = six.BytesIO(b'File upload contents.')
  >>> # \xc3\xb8 is UTF-8 for a small letter o with slash
  >>> # Still, we must decode it using latin-1 according to HTTP/1.1.
  >>> aFieldStorage = FieldStorageStub(myfile, filename=b'rand\xc3\xb8m.txt'.decode('latin-1'),
  ...     headers={'Content-Type': 'text/x-dummy'})
  >>> file_obj = file_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> file_obj.data
  b'File upload contents.'
  >>> file_obj.filename.encode('utf-8')
  b'rand\xc3\xb8m.txt'

Content type from headers sent by browser should be ignored::

  >>> file_obj.contentType != 'text/x-dummy'
  True

  >>> open_files.append(get_file('image.jpg'))
  >>> aFieldStorage = FieldStorageStub(open_files[-1], filename='random.png', headers={'Content-Type': 'image/x-dummy'})
  >>> image_obj = image_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> image_obj.data == image_data
  True
  >>> image_obj.filename
  'random.png'
  >>> image_obj.contentType != 'image/x-dummy'
  True


However, a zero-length, unnamed FileUpload results in the field's missing_value
being returned::

  >>> myfile = six.BytesIO(b'')
  >>> aFieldStorage = FieldStorageStub(myfile, filename='', headers={'Content-Type': 'application/octet-stream'})
  >>> field_value = file_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> field_value is IContent['file_field'].missing_value
  True
  >>> field_value = image_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> field_value is IContent['image_field'].missing_value
  True

If the file has already been uploaded and the user selects 'Keep Existing File'
in the widget, the widget will include 'action':'nochange' in the form post,
and the converter will always set the value to z3c.form.interfaces.NOT_CHANGED::

  >>> file_widget.request.form['widget.name.file.action'] = 'nochange'
  >>> file_converter.toFieldValue(u'') is NOT_CHANGED
  True
  >>> image_widget.request.form['widget.name.image.action'] = 'nochange'
  >>> image_converter.toFieldValue(u'') is NOT_CHANGED
  True

On validation errors, file uploads are stored in a temporary storage. The id of the temporarily stored file is given
by file_upload_id and action is set to 'nochange'.
The widget returns the temporary file on `extract` as Named[Blob](File|Image) and the dataconverter will simply use it

    >>> file_widget.request.form['widget.name.file.action'] = 'nochange'
    >>> file_widget.request.form['widget.name.file.file_upload_id'] = '5c6cc90ce82941919daaeb62700e079a'
    >>> file_converter.toFieldValue(NamedFile(data=b'testfile', filename=u'test.txt'))
    <plone.namedfile.file.NamedFile object at ...>

    >>> image_widget.request.form['widget.name.file.action'] = 'nochange'
    >>> image_widget.request.form['widget.name.file.file_upload_id'] = '5c6cc90ce82941919daaeb62700e079a'
    >>> file_converter.toFieldValue(NamedImage(data=b'testimage', filename=u'test.jpg'))
    <plone.namedfile.file.NamedImage object at ...>


The Base64Converter for Bytes fields
------------------------------------

There is another converter, which converts between a NamedFile or file upload
instance and base64 encoded data, which can be stored in a Bytes field::

  >>> from zope import schema
  >>> from zope.interface import implementer, Interface
  >>> class IBytesContent(Interface):
  ...     file_field = schema.Bytes(title=u"File")
  ...     image_field = schema.Bytes(title=u"Image")

  >>> from plone.formwidget.namedfile.converter import Base64Converter
  >>> provideAdapter(Base64Converter)

  >>> from zope.component import getMultiAdapter
  >>> from z3c.form.interfaces import IDataConverter

  >>> bytes_file_converter = getMultiAdapter(
  ...     (IBytesContent['file_field'], file_widget),
  ...     IDataConverter
  ... )
  >>> bytes_image_converter = getMultiAdapter(
  ...     (IBytesContent['image_field'], image_widget),
  ...     IDataConverter
  ... )

A value of None or '' results in the field's missing_value being returned::

  >>> bytes_file_converter.toFieldValue(u'') is IBytesContent['file_field'].missing_value
  True
  >>> bytes_file_converter.toFieldValue(None) is IBytesContent['file_field'].missing_value
  True

  >>> bytes_image_converter.toFieldValue(u'') is IBytesContent['image_field'].missing_value
  True
  >>> bytes_image_converter.toFieldValue(None) is IBytesContent['image_field'].missing_value
  True

A named file/image instance is returned as Base 64 encoded string in the
following form::

  filenameb64:BASE64_ENCODED_FILENAME;data64:BASE64_ENCODED_DATA

Like so::

  >>> bytes_file_converter.toFieldValue(
  ...     NamedFile(data=b'testfile', filename=u'test.txt'))
  b'filenameb64:dGVzdC50eHQ=;datab64:dGVzdGZpbGU='
  >>> bytes_image_converter.toFieldValue(
  ...     NamedImage(data=b'testimage', filename=u'test.png'))
  b'filenameb64:dGVzdC5wbmc=;datab64:dGVzdGltYWdl'

A Base 64 encoded structure like descibed above is converted to the appropriate
type::

  >>> afile = bytes_file_converter.toWidgetValue(
  ...     b'filenameb64:dGVzdC50eHQ=;datab64:dGVzdGZpbGU=')
  >>> afile
  <plone.namedfile.file.NamedFile object at ...>
  >>> afile.data
  b'testfile'
  >>> afile.filename
  'test.txt'

  >>> aimage = bytes_image_converter.toWidgetValue(
  ...     b'filenameb64:dGVzdC5wbmc=;datab64:dGVzdGltYWdl')
  >>> aimage
  <plone.namedfile.file.NamedImage object at ...>
  >>> aimage.data
  b'testimage'
  >>> aimage.filename
  'test.png'

Finally, some tests with image uploads converted to the field value.

Convert a file upload to the Base 64 encoded field value and handle the
filename too::


  >>> myfile = six.BytesIO(b'File upload contents.')
  >>> # \xc3\xb8 is UTF-8 for a small letter o with slash
  >>> # Still, we must decode it using latin-1 according to HTTP/1.1.
  >>> aFieldStorage = FieldStorageStub(myfile, filename=b'rand\xc3\xb8m.txt'.decode('latin-1'),
  ...     headers={'Content-Type': 'text/x-dummy'})
  >>> bytes_file_converter.toFieldValue(FileUpload(aFieldStorage))
  b'filenameb64:cmFuZMO4bS50eHQ=;datab64:RmlsZSB1cGxvYWQgY29udGVudHMu'

A zero-length, unnamed FileUpload results in the field's missing_value
being returned::

  >>> myfile = six.BytesIO(b'')
  >>> aFieldStorage = FieldStorageStub(myfile, filename='', headers={'Content-Type': 'application/octet-stream'})
  >>> field_value = bytes_file_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> field_value is IBytesContent['file_field'].missing_value
  True
  >>> field_value = bytes_image_converter.toFieldValue(FileUpload(aFieldStorage))
  >>> field_value is IBytesContent['image_field'].missing_value
  True


Rendering Bytes field widgets
-----------------------------

The widgets let the user to upload file and image data and select, if previous data should be kept, deleted or overwritten.

First, let's do the setup::

  >>> @implementer(IBytesContent, IImageScaleTraversable, IAttributeAnnotatable)
  ... class BytesContent(object):
  ...     def __init__(self, file, image):
  ...         self.file_field = file
  ...         self.image_field = image
  ...         # modification time is needed for a check in scaling:
  ...         self._p_mtime = DateTime()
  ...         self.path = '/content2'
  ...
  ...     def absolute_url(self):
  ...         return root_url + self.path
  ...
  ...     def Title(self):
  ...         return 'A content item'

  >>> content = BytesContent(None, None)

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
  ...         IBytesContent['{0}_field'.format(widget_type)],
  ...         make_request()
  ...     )
  ...     widget.context = context
  ...     widget.id = 'widget.id.{0}'.format(widget_type)
  ...     widget.name = 'widget.name.{0}'.format(widget_type)
  ...
  ...     if set_widget_value:
  ...         converter = globals()['bytes_{0}_converter'.format(widget_type)]
  ...         value = getattr(context, '{0}_field'.format(widget_type))
  ...         widget.value = converter.toWidgetValue(value)
  ...
  ...     return widget

  >>> file_widget = setup_widget('file', content, True)
  >>> image_widget = setup_widget('image', content)


Our content has no value yet::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <span id="widget.id.file" class="named-file-widget required bytes-field">
      <input type="file" id="widget.id.file-input" name="widget.name.file" />
  </span>

  >>> image_widget.update()
  >>> print(image_widget.render())
  <span id="widget.id.image" class="named-image-widget required bytes-field">
      <input type="file" id="widget.id.image-input" name="widget.name.image" />
  </span>


Let's upload data::

  >>> data = six.BytesIO(b'file 1 content.')
  >>> field_storage = FieldStorageStub(data, filename='file1.txt')
  >>> upload = FileUpload(field_storage)

  >>> file_widget.request = make_request(form={'widget.name.file': upload})
  >>> file_widget.update()
  >>> uploaded = file_widget.extract()
  >>> uploaded
  <ZPublisher.HTTPRequest.FileUpload ...>

  >>> content.file_field = bytes_file_converter.toFieldValue(uploaded)
  >>> content.file_field
  b'filenameb64:ZmlsZTEudHh0;datab64:ZmlsZSAxIGNvbnRlbnQu'

Check that we have a good image that PIL can handle::

  >>> import PIL.Image
  >>> open_files.append(get_file('image.jpg'))
  >>> PIL.Image.open(open_files[-1])
  <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=500x200 at ...>
  >>> open_files.append(get_file('image.jpg'))
  >>> field_storage = FieldStorageStub(open_files[-1], filename='image.jpg')
  >>> upload = FileUpload(field_storage)

  >>> image_widget.request = make_request(form={'widget.name.image': upload})
  >>> image_widget.update()
  >>> uploaded = image_widget.extract()
  >>> uploaded
  <ZPublisher.HTTPRequest.FileUpload ...>

  >>> content.image_field = bytes_image_converter.toFieldValue(uploaded)
  >>> content.image_field
  b'filenameb64:aW1hZ2UuanBn;datab64:/9j/4AAQSkZJRgABAQEAYABgAAD/...'

Note that PIL cannot open this bytes image, so we cannot scale it::

  >>> try:
  ...     PIL.Image.open(six.BytesIO(content.image_field))
  ... except Exception as e:
  ...     print(e)
  cannot identify image file...

Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content, True)
  >>> image_widget = setup_widget('image', content, True)


The upload shows up in the rendered widget::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required bytes-field">...
  <a href="http://127.0.0.1/content2/++widget++widget.name.file/@@download/file1.txt" >file1.txt</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> image_widget.update()
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required bytes-field">...
  <a href="http://127.0.0.1/content2/++widget++widget.name.image/@@download/image.jpg" >image.jpg</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...

Like we said, we cannot scale this bytes image, so the thumb tag is empty::

  >>> print(image_widget.thumb_tag)

Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content)
  >>> image_widget = setup_widget('image', content)


Now overwrite with other data::

  >>> data = six.BytesIO(b'random file content')
  >>> field_storage = FieldStorageStub(data, filename='plone.pdf')
  >>> upload = FileUpload(field_storage)

  >>> file_widget.request = make_request(form={'widget.name.file': upload, 'widget.name.file.action': 'replace'})
  >>> file_widget.update()
  >>> uploaded = file_widget.extract()
  >>> uploaded
  <ZPublisher.HTTPRequest.FileUpload ...>

  >>> content.file_field = bytes_file_converter.toFieldValue(uploaded)
  >>> content.file_field
  b'filenameb64:cGxvbmUucGRm;datab64:cmFuZG9tIGZpbGUgY29udGVudA=='


  >>> data = six.BytesIO(b'no image')
  >>> field_storage = FieldStorageStub(data, filename='logo.tiff')
  >>> upload = FileUpload(field_storage)

  >>> image_widget.request = make_request(form={'widget.name.image': upload, 'widget.name.image.action': 'replace'})
  >>> image_widget.update()
  >>> uploaded = image_widget.extract()
  >>> uploaded
  <ZPublisher.HTTPRequest.FileUpload ...>

  >>> content.image_field = bytes_file_converter.toFieldValue(uploaded)
  >>> content.image_field
  b'filenameb64:bG9nby50aWZm;datab64:bm8gaW1hZ2U='


Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content, True)
  >>> image_widget = setup_widget('image', content, True)


The new image/file shows up in the rendered widget::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required bytes-field">...
  <a href="http://127.0.0.1/content2/++widget++widget.name.file/@@download/plone.pdf" >plone.pdf</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> image_widget.update()
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required bytes-field">...
  <a href="http://127.0.0.1/content2/++widget++widget.name.image/@@download/logo.tiff" >logo.tiff</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...


Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content)
  >>> image_widget = setup_widget('image', content)

#  >>> interact(locals())

Resubmit, but keep the data::

  >>> file_widget.request = make_request(form={'widget.name.file': '', 'widget.name.file.action': 'nochange'})
  >>> file_widget.update()
  >>> uploaded = file_widget.extract()
  >>> uploaded
  <plone.namedfile.file.NamedFile object at ...>

  >>> content.file_field = bytes_file_converter.toFieldValue(uploaded)
  >>> content.file_field
  b'filenameb64:cGxvbmUucGRm;datab64:cmFuZG9tIGZpbGUgY29udGVudA=='


  >>> image_widget.request = make_request(form={'widget.name.image': '', 'widget.name.image.action': 'nochange'})
  >>> image_widget.update()
  >>> uploaded = image_widget.extract()
  >>> uploaded
  <plone.namedfile.file.NamedFile object at ...>

  >>> content.image_field = bytes_file_converter.toFieldValue(uploaded)
  >>> content.image_field
  b'filenameb64:bG9nby50aWZm;datab64:bm8gaW1hZ2U='


Prepare for a new request cycle::

  >>> file_widget = setup_widget('file', content, True)
  >>> image_widget = setup_widget('image', content, True)


The previous image/file should be kept::

  >>> file_widget.update()
  >>> print(file_widget.render())
  <... id="widget.id.file" class="named-file-widget required bytes-field">...
  <a href="http://127.0.0.1/content2/++widget++widget.name.file/@@download/plone.pdf" >plone.pdf</a>...
  <input type="radio"... id="widget.id.file-nochange"...
  <input type="radio"... id="widget.id.file-replace"...
  <input type="file"... id="widget.id.file-input"...

  >>> image_widget.update()
  >>> print(image_widget.render())
  <... id="widget.id.image" class="named-image-widget required bytes-field">...
  <a href="http://127.0.0.1/content2/++widget++widget.name.image/@@download/logo.tiff" >logo.tiff</a>...
  <input type="radio"... id="widget.id.image-nochange"...
  <input type="radio"... id="widget.id.image-replace"...
  <input type="file"... id="widget.id.image-input"...


The Download view on Bytes fields
---------------------------------
::

  >>> @implementer(IBytesContent)
  ... class BytesContent(object):
  ...     def __init__(self, file, image):
  ...         self.file_field = file
  ...         self.image_field = image
  ...         self.path = '/content3'
  ...
  ...     def absolute_url(self):
  ...         return root_url + self.path

  >>> content = BytesContent(
  ...     NamedFile(data=b"testfile", filename=u"test.txt"),
  ...     NamedImage(data=b"testimage", filename=u"test.jpg"))

  >>> from z3c.form.widget import FieldWidget

  >>> bytes_file_widget = FieldWidget(IBytesContent['file_field'], NamedFileWidget(make_request()))
  >>> bytes_file_widget.context = content

  >>> bytes_image_widget = FieldWidget(IBytesContent['image_field'], NamedImageWidget(make_request()))
  >>> bytes_image_widget.context = content

  >>> request = make_request()
  >>> view = Download(bytes_file_widget, request)
  >>> view()
  b'testfile'

  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''test.txt"

  >>> view = Download(bytes_image_widget, request)
  >>> view()
  b'testimage'

  >>> request.response.getHeader('Content-Disposition')
  "attachment; filename*=UTF-8''test.jpg"


Range support
-------------

Checking for partial requests support::

  >>> request = make_request()
  >>> view = Download(bytes_file_widget, request)
  >>> view()
  b'testfile'
  >>> request.response.getHeader('Content-Length')
  '8'
  >>> request.response.getHeader('Accept-Ranges')
  'bytes'

Request a specific range::

  >>> request = make_request(environ={'HTTP_RANGE': 'bytes=0-3'})
  >>> view = Download(bytes_file_widget, request)
  >>> view()
  b'test'
  >>> request.response.getStatus()
  206

The Content-Length header now indicates the size of the requested range (and not the full size of the image).
The Content-Range response header indicates where in the full resource this partial message belongs.::

  >>> request.response.getHeader('Content-Length')
  '4'
  >>> request.response.getHeader('Content-Range')
  'bytes 0-3/8'


The validator
-------------

If the user clicked 'replace' but did not provide a file, we want to get a
validation error::

  >>> from plone.formwidget.namedfile.validator import NamedFileWidgetValidator

If 'action' is omitted and the value is None, we should get a validation error
only when the field is required::

  >>> request = make_request(form={'widget.name.file': myfile})
  >>> validator = NamedFileWidgetValidator(content, request, None, IContent['file_field'], file_widget)
  >>> validator.validate(None) is None
  Traceback (most recent call last):
  ...
  zope.schema._bootstrapinterfaces.RequiredMissing...
  >>> IContent['file_field'].required = False
  >>> validator.validate(None) is None
  True

However, if it is set to 'replace' and there is no value provided, we get the
InvalidState exception from validator.py (its docstring is displayed to the
user)::

  >>> request = make_request(form={'widget.name.file': myfile, 'widget.name.file.action': 'replace'})
  >>> validator = NamedFileWidgetValidator(content, request, None, IContent['file_field'], file_widget)
  >>> validator.validate(None)
  Traceback (most recent call last):
  ...
  plone.formwidget.namedfile.validator.InvalidState

If we provide a file, all is good::

  >>> request = make_request(form={'widget.name.file': myfile, 'widget.name.file.action': 'replace'})
  >>> validator = NamedFileWidgetValidator(content, request, None, IContent['file_field'], file_widget)
  >>> validator.validate(file_obj) is None
  True

Similarly, if we really wanted to remove the file, we won't complain, unless
we again make the field required::

  >>> request = make_request(form={'widget.name.file': myfile, 'widget.name.file.action': 'remove'})
  >>> validator = NamedFileWidgetValidator(content, request, None, IContent['file_field'], file_widget)
  >>> validator.validate(None) is None
  True
  >>> IContent['file_field'].required = True
  >>> validator.validate(None) is None
  Traceback (most recent call last):
  ...
  zope.schema._bootstrapinterfaces.RequiredMissing...


The Download URL
----------------

The download URL has the following format::

  $CONTEXT_URL/[$FORM/]++widget++$WIDGET/@@download[/$FILENAME]

The download URL without a form and without a value::

  >>> content = Content(None, None)
  >>> file_widget = NamedFileFieldWidget(IContent['file_field'], make_request())
  >>> file_widget.context = content
  >>> file_widget.name
  'file_field'
  >>> file_widget.download_url
  'http://127.0.0.1/content1/++widget++file_field/@@download'

Now we add a value::

  >>> content.file_field = NamedFile(data=b'My file data', filename=u'data.txt')
  >>> file_widget.value = content.file_field
  >>> file_widget.download_url
  'http://127.0.0.1/content1/++widget++file_field/@@download/data.txt'

And a form::

  >>> class TestForm(object):
  ...     pass
  >>> form = TestForm()
  >>> form.__name__ = 'test-form'
  >>> file_widget.form = form
  >>> file_widget.request = make_request(content.path + '/' + form.__name__)
  >>> file_widget.download_url
  'http://127.0.0.1/content1/test-form/++widget++file_field/@@download/data.txt'

The download URL stays the same even if the request URL does not point to
the context and/or form the widget is bound to. For example: we're rendering
a custom view of a folder which lists all the contained files. The code for this
view would get all ``Content`` instances on the folder and then use our widget
(maybe inside a form) to display the information about each file::

  >>> file_widget.request = make_request('/folder-1/custom-folder-view')
  >>> file_widget.download_url
  'http://127.0.0.1/content1/test-form/++widget++file_field/@@download/data.txt'

The download URL also stays the same also when the field belongs to a group of
a group form. This behavior assumes that groups are used to map fieldsets on a
form (and not a group of separate objects)::

  >>> from z3c.form.group import Group
  >>> group = Group(content, file_widget.request, form)
  >>> group.__name__ = 'test-fieldset'
  >>> file_widget.form = group
  >>> file_widget.download_url
  'http://127.0.0.1/content1/test-form/++widget++file_field/@@download/data.txt'

Some times the context does not have an URL i.e ``context.absolute_url`` is
not implemented. In these cases the download URL will be::

  $REQUEST_URL/++widget++$WIDGET/@@download[/$FILENAME]

Like in this case::

  >>> class Context(object):
  ...     pass
  >>> file_widget.context = Context()
  >>> file_widget.request = make_request('/some/path')
  >>> file_widget.download_url
  'http://127.0.0.1/some/path/++widget++file_field/@@download/data.txt'

If we change the name of the widget the download URL will reflect that::

  >>> file_widget.name = 'my_widget'
  >>> file_widget.download_url
  'http://127.0.0.1/some/path/++widget++my_widget/@@download/data.txt'

Close all open file handlers:

  >>> ignore = [x.close() for x in open_files]
