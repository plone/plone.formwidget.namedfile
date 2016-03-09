# -*- coding: utf-8 -*-
import doctest
import unittest
# import interlude


def setUp(self):
    """Test setUp based on z3c.form.testing.setUp minus their globals.
    """
    from zope.component.testing import setUp
    setUp()
    from zope.container.testing import setUp
    setUp()
    from zope.component import hooks
    hooks.setHooks()
    from zope.traversing.testing import setUp
    setUp()

    from zope.publisher.browser import BrowserLanguages
    from zope.publisher.interfaces.http import IHTTPRequest
    from zope.i18n.interfaces import IUserPreferredLanguages
    import zope.component
    zope.component.provideAdapter(
        BrowserLanguages, [IHTTPRequest], IUserPreferredLanguages)

    from zope.site.folder import rootFolder
    site = rootFolder()
    from zope.site.site import LocalSiteManager
    from zope.component.interfaces import ISite
    if not ISite.providedBy(site):
        site.setSiteManager(LocalSiteManager(site))
    hooks.setSite(site)


def tearDown(self):
    """Test tearDown based on z3c.form.testing.tearDown minus their globals.
    """
    from zope.testing import cleanup
    from zope.component import hooks
    cleanup.cleanUp()
    hooks.resetHooks()
    hooks.setSite()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'widget.rst',
        setUp=setUp,
        tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        encoding='utf-8',
        # globs={'interact': interlude.interact},
    ))
    return suite
