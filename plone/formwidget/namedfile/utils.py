# -*- coding: utf-8 -*-
from BTrees.OOBTree import OOBTree
from datetime import datetime
from datetime import timedelta
from plone.formwidget.namedfile.interfaces import IFileUploadMap
from random import randint
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from ZPublisher.HTTPRequest import FileUpload


FILE_UPLOAD_MAP_KEY = 'file_upload_map'
FILE_UPLOAD_EXPIRATION_TIME = 30*60  # seconds
FALLBACK_DATE = datetime(2000, 2, 2)


def is_file_upload(item):
    """Check if ``item`` is a file upload.
    """
    return isinstance(item, FileUpload)


@implementer(IFileUploadMap)
@adapter(Interface)
class FileUploadMap(object):
    """Temporary storage adapter for file uploads.
    To be used to not need to re-upload files after form submission errors.
    """

    def __init__(self, context):
        self.context = context

    @property
    def upload_map(self):
        annotations = IAnnotations(self.context)
        # file_upload_id is of type long, therefore we need a OOBTree
        upload_map = annotations.get(FILE_UPLOAD_MAP_KEY, OOBTree())

        for key, val in upload_map.items():
            if val.get('dt', FALLBACK_DATE) < (
                datetime.now() - timedelta(
                    seconds=FILE_UPLOAD_EXPIRATION_TIME
                )
            ) and randint(0, 5) == 0:  # Avoid conflict errors by deleting only every fifth time  # noqa
                # Delete expired files or files without timestamp
                del upload_map[key]
        return upload_map
