from BTrees.OOBTree import OOBTree
from Products.CMFPlone.interfaces import IImagingSchema
from ZPublisher.HTTPRequest import FileUpload
from datetime import datetime
from datetime import timedelta
from persistent.dict import PersistentDict
from plone.formwidget.namedfile.interfaces import IFileUploadTemporaryStorage
from plone.registry.interfaces import IRegistry
from random import randint
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implementer


FILE_UPLOAD_MAP_KEY = "file_upload_map"
FILE_UPLOAD_EXPIRATION_TIME = 30 * 60  # seconds
FALLBACK_DATE = datetime(2000, 2, 2)
CLEANUP_INTERVAL = 5

def is_file_upload(item):
    """Check if ``item`` is a file upload."""
    return isinstance(item, FileUpload)


@implementer(IFileUploadTemporaryStorage)
@adapter(Interface)
class FileUploadTemporaryStorage:
    """Temporary storage adapter for file uploads.
    To be used to not need to re-upload files after form submission errors.
    """

    def __init__(self, context):
        self.context = context

    @property
    def upload_map(self):
        annotations = IAnnotations(self.context)
        upload_map = annotations.setdefault(FILE_UPLOAD_MAP_KEY, OOBTree())
        return upload_map

    def cleanup(self, force=False):
        """Remove obsolete temporary uploads.

        To avoid conflict errors, files are deleted on every ~5th method call.
        Use force to make sure all expired files are deleted
        """
        upload_map = self.upload_map
        expiration_limit = datetime.now() - timedelta(seconds=FILE_UPLOAD_EXPIRATION_TIME)
        # Avoid conflict errors by deleting only every fifth time
        delete = force or randint(1, CLEANUP_INTERVAL) == 1
        for key in list(upload_map.keys()):
            dt = upload_map[key].get('dt', FALLBACK_DATE)
            if dt < expiration_limit and delete:
                # Delete expired files or files without timestamp
                del upload_map[key]


def get_scale_infos():
    """Returns a list of (name, width, height) 3-tuples of the
    available image scales.
    """
    registry = getUtility(IRegistry)
    imaging_settings = registry.forInterface(IImagingSchema, prefix="plone")
    allowed_sizes = imaging_settings.allowed_sizes

    def split_scale_info(allowed_size):
        name, dims = allowed_size.split(" ")
        width, height = list(map(int, dims.split(":")))
        return name, width, height

    return [split_scale_info(size) for size in allowed_sizes]
