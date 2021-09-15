Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.0.0a4 (2021-09-15)
--------------------

Bug fixes:


- Fix issue where expired temporary uploads have not been removed when calling FileUploadTemporaryStorage.cleanup() (https://github.com/plone/plone.formwidget.namedfile/issues/52) [fRiSi] (#52)
- Make CLEANUP_INTERVAL patchable and fix condition (https://github.com/plone/plone.formwidget.namedfile/issues/54) (#54)


3.0.0a3 (2021-07-28)
--------------------

New features:


- Add to generate configured Plone image scales on save when environment variable PLONE_SCALE_GENERATE_ON_SAVE=1 is set. With the default Plone configuration, this effectively removes on-demand image scaling on GET requests. [datakurre] (#43)


Bug fixes:


- Fix issue where already uploaded images were lost when file validation error occurs (https://github.com/plone/plone.formwidget.namedfile/issues/46)  [fRiSi] (#46)


3.0.0a2 (2021-06-30)
--------------------

Bug fixes:


- Support for Pillow 8 in tests. [jensens] (#50)


3.0.0a1 (2021-06-14)
--------------------

Bug fixes:


- Fix `NamedFileWidget` bug when trying to create value from `None`. [vangheem] (#35)
- Don't check for hard coded image size in test.
  [agitator] (#40)
- Overhaul for Plone 6: Skip Python 2 compatibility, pyupgrade, isort, black, manual cleanup. [jensens] (#47)


2.1.0 (2020-06-24)
------------------

New features:


- Range support (https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests)
  [mamico] (#44)


2.0.11 (2020-04-20)
-------------------

Bug fixes:


- Minor packaging updates. (#1)


2.0.10 (2019-12-11)
-------------------

Bug fixes:


- set widget value to z3c.form.interfaces.NOT_CHANGED when the user selects 'Keep Existing File' in the widget, so z3c.form understands the field has not changed [flipmcf] (#41)


2.0.9 (2019-03-28)
------------------

Bug fixes:


- Only use the new feature for keeping an already uploaded image when it is a POST request.
  Fixes auto csrf error in `site-controlpanel <https://github.com/plone/Products.CMFPlone/issues/2628>`_
  and `personal-information <https://github.com/plone/Products.CMFPlone/issues/2709>`_ page.
  [maurits] (#2628)


2.0.8 (2019-01-08)
------------------

Bug fixes:


- Close files, so no resource warnings are shown. [gforcada] (#36)
- Initialize towncrier. [gforcada] (#2548)


2.0.7 (2018-11-05)
------------------

Bug fixes:

- Python 2 / 3 compatibility
  [ale-rt, pbauer, davisagli]


2.0.6 (2018-09-26)
------------------

Bug fixes:

- Prepare for Python 2 / 3 compatibility
  [ale-rt, pbauer]

- On form validation errors after submitting, keep the already uploaded image.
  [thet]


2.0.5 (2017-11-26)
------------------

Bug fixes:

- remove mention of "retina" (https://github.com/plone/Products.CMFPlone/issues/2123)
  [tkimnguyen]


2.0.4 (2017-09-05)
------------------

Bug fixes:

- Fixing UnicodeError when the @@z3cform_validate_field view sends
  a filename with type unicode. (collective.easyform in our case)
  [karalics]

2.0.3 (2017-07-03)
------------------

Bug fixes:

- Fix issue where display widget failed to render file fields located
  on form fieldsets, because of broken generated download url
  [datakurre]


2.0.2 (2016-08-15)
------------------

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


2.0.1 (2016-06-07)
------------------

Bug fixes:

- Make the download URL independent of the request URL. The format of the
  URL will always be:
  ``$CONTEXT_URL/[$FORM/]++widget++$WIDGET/@@download[/$FILENAME]``
  [rafaelbco]


2.0.0 (2016-05-09)
------------------

Incompatibilities:

- Removed no longer needed ``thumb_width`` and ``thumb_height`` from
  the image widget.  ``width`` and ``height`` are still there.
  [jladage, maurits]

New:

- On the edit form, show a thumbnail instead of rendering the image in
  full size.  To make this prettier on retina screens, we actually
  load the larger preview scale and let it use the width and height of
  the thumbnail.
  Fixes https://github.com/plone/plone.formwidget.namedfile/issues/21
  [jladage, maurits]

- Use ``plone.app.testing`` in tests.  [maurits]


1.0.15 (2016-03-22)
-------------------

Fixes:

- Fix issue, where NamedFileWidget and NamedImageWidget on
  ``zope.schema.ASCII`` fields cleared the field values on resubmit
  with action ``nochange``.
  Fixes: plone/Products.CMFPlone#1144
  [thet]


1.0.14 (2016-02-12)
-------------------

New:

- Use plone i18n domain.
  See https://github.com/plone/plone.formwidget.namedfile/pull/18
  [staeff]

- Add Finnish translations.
  [petri]

Fixes:

- Specify doctest encoding and make doctest more robust against formatting changes.
  [thet]

- Replace deprecated ``zope.testing.doctestunit`` import with ``doctest`` module from stdlib.
  [thet]


1.0.13 (2015-03-21)
-------------------

- Do not use format() since it will break for Python 2.6.
  [timo]


1.0.12 (2015-02-01)
-------------------

- Add Base64 data converter for NamedImage and NamedFile widgets on ASCII
  fields with base64 encoded data and filename. Now the NamedImage and
  NamedFile widgets can be used with ``zope.schema.ASCII`` fields.
  [thet]

- PEP 8.
  [thet]


1.0.11 (2014-09-29)
-------------------

- Ignore contentType sent by browser for file uploads.
  See https://github.com/plone/plone.formwidget.namedfile/issues/9
  [lgraf]

- The context should be ignored, but not the value if explicitly set.
  plone.multilingual will set the value for language-independent fields
  when translating.
  [regebro]


1.0.10 (2014-05-26)
-------------------

- Catch mimetype exception, avoid site error if mimetype is not recognized.
  [thomasdesvenain]

- Avoid error if widget is not used in acquisition context.
  [thomasdesvenain]

- Add Italian translation
  [giacomos]


1.0.9 (2014-01-27)
------------------

- Fix fr translation for "Remove image".


1.0.8 (2013-12-07)
------------------

- The _mimetype property in NamedFileWidget would fail on attempting
  to render after a validation failure when it tried to lookup a
  mimetype with the wrong method. Result was a malformed mimetype
  exception. Fixes #13798.
  [smcmahon]

- Display icon and content type name on widget.
  [thomasdesvenain]

- Internationalized size on file and image widget.
  [thomasdesvenain]


1.0.7 (2013-08-13)
------------------

- Add optional force parameter to the validate method to match a change
  in the z3c.form API.


1.0.6 (2013-05-26)
------------------

* added dutch translation
  [maartenkling]

1.0.5 (2013-03-05)
------------------

- Nothing changed yet.


1.0.4 (2013-01-01)
------------------

* added french translation
  [tschanzt]

* added danish translation
  https://github.com/plone/plone.formwidget.namedfile/pull/2
  [tmog]

1.0.3 (2012-10-09)
------------------

* Use download_url for display templates also
  [lentinj]

* Fix the download view for widgets whose form has a custom getContent method.
  [davisagli]

1.0.2 (2011-09-24)
------------------
* Added Simplified Chinese translation.
  [jianaijun]

* Added pt_BR translation.
  [rafaelbco, davisagli]

* Additional unit tests for download view
  [lentinj]

1.0.1 (2011-07-02)
------------------

* Don't need to ask parent for widget name anymore, since ++widget++ traverser
  will understand full widget names.
  [lentinj]

1.0 (2011-04-30)
----------------

* Allow field widget to display without absolute_url.
  [elro]

1.0b10 (2011-03-02)
-------------------

* Use what the parent considers to be the widget name if available.
  Without which named images in dexterity behaviors break.
  [lentinj, elro]

1.0b9 (2011-02-11)
------------------

* Fix handling of unicode filenames when converting or quoting the URL.
  Fixes http://code.google.com/p/dexterity/issues/detail?id=148
  [rossp, mj]

* Added Spanish translations.
  [dukebody]

* Added german translations.
  [jbaumann]


1.0b8 (2010-10-01)
------------------

* Avoid showing validation errors during KSS validation, as the file is not
  uploaded in this case.
  [davisagli]

* Don't use the action from the request when the form submission succeeded.
  (In that case we always want "keep existing image")
  [davisagli]

1.0b7 (2010-08-05)
------------------

* Fix Wichert's previous fix to check ignoreContext the correct way.
  [davisagli]

1.0b6 (2010-05-17)
------------------

* Do not query the datamanager if we should ignore the context. Fixes
  http://code.google.com/p/dexterity/issues/detail?id=120
  [wichert]

1.0b5 (2010-04-19)
------------------

* Avoiding reading file uploads to determine their size.
  [wichert]

1.0b4 (2010-04-07)
------------------

* Rename nochange to action, since the field was being used to specify
  which action to take.
  [wichert]

* Disabled state was being applied to the wrong tag (span instead of the
  input) for images and files, and we're not using tabindex anymore.
  [limi]

1.0b3 (2010-01-25)
------------------

* Fix bug where fields that failed validation for requiredness mistakenly
  interpret the empty FileUpload in the request as a real value.
  [davisagli]

* Fix bug where fields were not validated for requiredness or field constraints.
  [davisagli]

* In lieu of real image scaling, at least make sure the thumbnail used on the
  image input widget has the correct aspect ratio.  Fixes
  http://code.google.com/p/dexterity/issues/detail?id=77
  [davisagli]

1.0b2 (2009-09-13)
------------------

* Make the widget more robust to validation errors elsewhere in the form.
  Fixes http://code.google.com/p/dexterity/issues/detail?id=76.
  [optilude]

1.0b1 (2009-08-02)
------------------

* Add option to remove files or images. This fixes dexterity issue #71:
  http://code.google.com/p/dexterity/issues/detail?id=71
  [wichert]


1.0a1 (2009-04-17)
------------------

* Initial release
