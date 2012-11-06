import re

from django import template
from django.conf import settings
from django.template.base import TextNode, NodeList, Node
from django.contrib.staticfiles.storage import staticfiles_storage

from compress.utils import get_file_extension


register = template.Library()


class CompressedTag(NodeList, Node):

    KWARG_RE = re.compile("([^=]+)=[\"']?([^\"']*)[\"']")
    QUOTE_RE = re.compile("['\"]")

    def __init__(self, parser, token):
        self.parser = parser
        self.kwargs = {}

        self.args = token.split_contents()
        self.tag_name = self.args.pop(0)
        self.set_name = self.QUOTE_RE.sub("", self.args.pop(0))

        self.parse_kwargs()

    def parse_kwargs(self):
        for arg in self.args:
            match = self.KWARG_RE.match(arg)

            if match:
                key, value = match.groups()
                self.kwargs[key] = value

    @property
    def debug(self):
        if "debug" in self.kwargs:
            return (self.kwargs["debug"].lower() == "true")
        else:
            return settings.DEBUG

    @property
    def template_name(self):
        file_extension = get_file_extension(self.set_name)
        return "compress/{0}_tag.html".format(file_extension)

    @property
    def file_set(self):
        return settings.COMPRESS_SETS[self.set_name]

    def sub_render(self, filename):
        args = self.kwargs.copy()
        args.update({ "path": staticfiles_storage.url(filename) })

        return template.loader.render_to_string(self.template_name, args)

    def __iter__(self):
        if self.debug:
            for filename in self.file_set:
                yield TextNode(self.sub_render(filename))
        else:
            yield TextNode(self.sub_render(self.set_name))


@register.tag
def compressed(parser, token):
    return CompressedTag(parser, token)
