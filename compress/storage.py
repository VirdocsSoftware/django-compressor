import re
import os
from urllib import unquote
from fnmatch import fnmatch
from datetime import datetime
from cStringIO import StringIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.utils import matches_patterns
from django.contrib.staticfiles.finders import BaseFinder, FileSystemFinder

from compress.compressor import get_compressor_class


class CompressedStorage(FileSystemStorage):

    patterns = (
        ("*.css", (
            r"""(url\(['"]{0,1}\s*(.*?)["']{0,1}\))""",
            r"""(@import\s*["']\s*(.*?)["'])""",
        )),
    )

    def __init__(self, *args, **kwargs):
        super(CompressedStorage, self).__init__(*args, **kwargs)
        self.finder = FileSystemFinder()
        self.compressor = get_compressor_class()()

        self._patterns = {}
        for extension, patterns in self.patterns:
            for pattern in patterns:
                compiled = re.compile(pattern)
                self._patterns.setdefault(extension, []).append(compiled)

    def path(self, name):
        found = self.finder.find(name)
        return found if found else name

    def delete(self, name):
        pass

    def modified_time(self, name):
        stamps = [os.stat(self.path(filename)).st_mtime
            for filename in settings.COMPRESS_SETS[name]]

        return datetime.fromtimestamp(max(stamps))

    def url_converter(self, filename):
        def converter(matchobj):
            matched, url = matchobj.groups()

            if url.startswith(('#', 'http:', 'https:', 'data:')):
                return matched

            joined_result = os.path.relpath(
                    os.path.join(
                        os.path.dirname(filename),
                        os.path.normpath(url)))

            return 'url("%s")' % unquote(joined_result)

        return converter

    def munge_file(self, filename, contents):
        for extension, patterns in self._patterns.items():
            if not fnmatch(filename, extension):
                continue

            for pattern in patterns:
                contents = pattern.sub(self.url_converter(filename), contents)

        return contents

    def _load_file(self, filename, buffer):
        contents = ""

        with open(self.path(filename), 'rb') as fp:
            contents = fp.read()

        buffer.write(self.munge_file(filename, contents))

    def _open(self, name, mode='rb'):
        buffer = StringIO()

        for filename in settings.COMPRESS_SETS[name]:
            self._load_file(filename, buffer)

        return ContentFile(self.compressor(buffer, filename))


class CompressedFileFinder(BaseFinder):

    def __init__(self, *args, **kwargs):
        super(CompressedFileFinder, self).__init__(*args, **kwargs)
        self.storage = CompressedStorage()

    def list(self, ignore_patterns):
        for filename in settings.COMPRESS_SETS.keys():
            if not matches_patterns(filename, ignore_patterns):
                yield filename, self.storage
