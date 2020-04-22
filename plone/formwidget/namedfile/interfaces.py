from z3c.form.interfaces import IWidget
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface


class INamedFileWidget(IWidget):
    """A widget for a named file field"""

    allow_nochange = schema.Bool(
        title="Allow user to keep existing data in lieu of uploading a file?"
    )
    filename = schema.TextLine(title="Name of the underlying file", required=False)
    filename_encoded = schema.TextLine(title="Filename, URL-encoded", required=False)
    file_size = schema.Int(title="Size in kb", required=True, default=0)
    download_url = schema.URI(title="File download URL", required=False)


class INamedImageWidget(INamedFileWidget):
    """A widget for a named image field"""

    width = schema.Int(title="Image width", min=0, required=False)
    height = schema.Int(title="Image height", min=0, required=False)
    thumb_tag = schema.Text(title="Thumbnail image tag", required=False)
    alt = schema.TextLine(title="Image alternative text", required=False)


class IFileUploadTemporaryStorage(Interface):
    """Temporary storage adapter for file uploads.
    To be used to not need to re-upload files after form submission errors.
    """

    upload_map = Attribute(
        """
        Mapping for temporary uploads.
        Key is a uuid4.hex value.
        The default storage is the annotation storage of the poral root.
    """
    )

    def cleanup():
        """Removes stale temporary uploads from the upload storage"""


class IScaleGenerateOnSave(Interface):
    """Marker interface on request for creating scales
    when NamedImageField has been used to save a new image file on content.
    """
