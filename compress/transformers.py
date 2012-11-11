import re
import os
from urllib import unquote
from fnmatch import fnmatch
from django.contrib.staticfiles.storage import CachedFilesMixin


class CSSURLTransformer(object):

    @staticmethod
    def can_handle(filename):
        return fnmatch(filename, "*.css")

    def __init__(self):
        self._patterns = [re.compile(pattern)
                for pattern in CachedFilesMixin.patterns[0][1]]

    def convert_func(self, filename):
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

    def __call__(self, filename, contents):
        for pattern in self._patterns:
            contents = pattern.sub(self.convert_func(filename), contents)

        return contents
