from subprocess import Popen, PIPE

from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from compress.utils import get_file_extension


class BaseCompressor(object):

    def args_for_file(self, filename):
        return []

    @property
    def compressor_command(self):
        try:
            return [settings.COMPRESSOR_COMMAND]
        except AttributeError:
            pass

        try:
            return self.DEFAULT_COMMAND
        except AttributeError:
            raise ImproperlyConfigured("No compressor command set")

    def __call__(self, contents, filename):
        command = self.compressor_command + self.args_for_file(filename)
        compressor = Popen(command, stdin=PIPE, stdout=PIPE)
        return compressor.communicate(contents.getvalue())[0]


class YUICompressor(BaseCompressor):

    DEFAULT_COMMAND = ["yui-compressor"]

    def args_for_file(self, filename):
        return ["--type={0}".format(get_file_extension(filename))]


def get_compressor_class():
    try:
        import_path = settings.STATICFILES_COMPRESSOR
    except AttributeError:
        raise ImproperlyConfigured("No compressor is configured. "
                "Set STATICFILES_COMPRESSOR in settings.py")

    try:
        dot = import_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured(
                "%s isn't a compressor module." % import_path)

    module, classname = import_path[:dot], import_path[dot+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured(
                'Error importing compressor module %s: "%s"' % (module, e))

    try:
        return getattr(mod, classname)
    except AttributeError:
        raise ImproperlyConfigured(
                'Compressor module "%s" does not define a "%s" class.' % (
                    module, classname))
