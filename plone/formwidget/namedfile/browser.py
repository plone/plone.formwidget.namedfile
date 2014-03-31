#-*- coding: utf-8 -*-

from Acquisition import aq_inner

from zope.component import getMultiAdapter
from zope.interface import implements

from z3c.form.interfaces import IDataManager

from plone.namedfile.utils import set_headers, stream_data


from Products.Five.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse, NotFound


class Download(BrowserView):

    """Download a file, via ../context/form/++widget++/@@download/filename
    """

    implements(IPublishTraverse)

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
            raise NotFound(
                "Cannot get the data file from a widget with no context")

        if self.context.form is not None:
            content = aq_inner(self.context.form.getContent())
        else:
            content = aq_inner(self.context.context)
        field = aq_inner(self.context.field)

        dm = getMultiAdapter((content, field,), IDataManager)
        file_ = dm.get()
        if file_ is None:
            raise NotFound(self, self.filename, self.request)

        if not self.filename:
            self.filename = getattr(file_, 'filename', None)

        set_headers(file_, self.request.response, filename=self.filename)
        return stream_data(file_)
