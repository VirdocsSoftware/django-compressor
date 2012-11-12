=================
Django Compressor
=================

This is an asset compression framework for Django. Asset compressors
concatenate and minify Javascript and CSS. While there are many other asset
compression frameworks for Django this framework attempts to stay as simple and
unobtrusive as possible while still supporting development and production
deployments.

Usage
=====
After using pip to install the package a few changes to ``settings.py`` will be
necessary. For best results it is recommended to use compress with Django's
cached staticfiles provider which will inject file hashes into the name of the
file.

The following changes should be made to your ``settings.py`` file::

    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
    STATICFILES_COMPRESSOR = 'compress.compressor.YUICompressor'

    STATICFILES_FINDERS = (
        ...,
        'compress.storage.CompressedFileFinder',
    )

    INSTALLED_APPS = (
        ...,
        "compress",
    )

**Note:** if you've already specified ``STATICFILES_FINDERS`` then just add
``compress.storage.CompressedFileFinder`` to the list.

The ``YUICompressor`` provider will require the you have the ``yui-compressor``
binary on your path. Setting that up is beyond the scope of this readme,
however most OS package managers have a package for yui-compressor.

Compress Sets
-------------
Compress uses compress sets that are configured in ``settings.py`` as well as a
custom template tag to support generation of CSS and JS tags in your templates.
To configure compress sets add a ``COMPRESS_SETS`` variable to your ``settings.py``
file like so::

    COMPRESS_SETS = {
        'print.css': [
            'css/print.css',
        ],
        'vendor.js': [
            'js/vendor/jquery-1.7.2.js',
        ]
    }

The key to the dictionary is the set name that will be used by the template
tag. The value for each key is a list of static files to be included in that
set. Paths are relative to the directories in ``STATICFILES_DIRS``.

The file extension for a set is important, this is how compress determines how
to compress your assets and which HTML tags to render.

Compress Tag
------------
Once compress is configured in ``settings.py`` the last step is to use the
``compressed`` template tag to actually include the assets in a template. The
first step is to load the ``compressed`` tag::

    {% load compressed %}

Finally, include compressed sets by name using the ``compressed`` tag::

    {% compressed 'print.css' %}

When your application is in DEBUG mode compress will render HTML tags for each
file in your compressed set, it will also forego any concatenation and
compression.

When your application is not in DEBUG mode compress will render a single tag
for each compressed set that links to a concatenated and minified version of
the asset.

Deploying Compress Applications
-------------------------------
To deploy an application using compress use the standard ``collectstatic``
management command. This will generate concatenated and minified versions of
your compress sets and place them alongside your other static files.

**Note:** Your uncompressed assets will also be added to the static files root
alongside your compressed assets. If there is anything secret in those files
you may want to remove them.

Optional Compress Tag Arguments
===============================
The compress tags supports keyword arguments. With the exception of the special
``debug`` argument, the keyword arguments are passed directly to the template
engine when it renders the tags.

Keyword arguments are any argument with a key followed by an = followed by a
single or double quoted string. For example, to create a print stylesheet::

    {% compressed 'print.css' media='print' %}

will render::

    <link href="print.css" rel="stylesheet" type="text/css" media="print" />

To support keyword arguments beyond media for CSS you will have to provide your
own templates. More on that below.

Debug Argument
--------------
The ``debug`` keyword argument is special. The compress renderer interprets this
as an override for the ``DEBUG`` flag in ``settings.py``. This can be used to
always render the complete tag list or to always render the compressed version.
Debug is used like any other keyword argument. The value is expected to be
either ``true`` or ``false``.

Extending Compress
==================
There are two primary ways to extend compress: template overrides and pluggable
compressors.

Template Overrides
------------------
Compress looks up templates based on the extension of the set name. For
example, if your set name is print.css then compress will try to load
``compress/css_tag.html`` from the template folder.

Compress ships with templates for CSS and Javascript which can be overridden by
providing your own templates in a compress folder in your application's
template location. Additional set types can be supported by providing
additional templates.

The template context in which the compress templates are rendered will always
have a ``path`` variable which is the path to the asset file. Any keyword
arguments passed to the ``compressed`` template tag will also be available.

Pluggable Compressors
---------------------
Out of the box compress supports yui-compressor. It is possible to extend
compress with your own compressors. A compressor is simply a callable class
that accepts two arguments. The first argument is a StringIO object with the
concatenated contents of the asset files. The original filename is the second
argument. The compressor is expected to provide a string-like object that can
be passed to Django's ``ContentFile``.

In the simplest of cases where the compressor does not need any special
arguments it is possible to set the following settings in your ``settings.py``
file and write no more code::

    COMPRESSOR_COMMAND = "your-compressor"
    STATICFILES_COMPRESSOR = 'compress.compressor.BaseCompressor'

If your compressor needs a few more arguments you can subclass ``BaseCompressor``
and provide your own implementation of ``args_for_file`` like so::

    class YUICompressor(BaseCompressor):

        DEFAULT_COMMAND = ["yui-compressor"]

        def args_for_file(self, filename):
            return ["--type={0}".format(get_file_extension(filename))]

In more complex cases just provide your own callable class who's initializer
takes no arguments.

Pluggable Transformers
----------------------
Transformers pre-process the concatenated files before they are handed to the
compressor. The original use-case was to fix URLs in CSS files in the same way
that the built-in staticfiles fixes URLs by adding the file hash to the name.

Transformers are callable classes with a ``can_handle`` static method which
takes a filename and returns a boolean value if the transformer can handle a
given file. If the transformer can handle the file it will be constructed with
no arguments and called with the filename as the first argument and a string
with the file contents as the second argument. The function should return the
transformed contents when it is finished.

All transformers that can handle a file will be run before the file is given to
the compressor.

To register a transformer append it to the list of transformers on an instance
of ``CompressedStorage`` like so::

    comp = CompressedStorage()
    comp.transformers.append(MyTransformerClass)
