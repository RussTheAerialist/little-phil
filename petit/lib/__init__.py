import os.path as path
from pkg_resources import resource_listdir
import importlib

class _BaseObject(object):
    def __init__(self, config):
        self._config = config

def load_module(parent, module_name):
    try:
        full_module_name = "{parent}.{module_name}".format(parent=parent,
                                                           module_name=module_name)

        module = importlib.import_module(full_module_name)
        return module
    except ImportError,ex:
        print ex
        return None

def glob_modules(parent, pred):
    for system in filter(pred, resource_listdir(parent, '')):
        (module_name, ext) = path.splitext(system)
        if ext == ".py":
            retval = load_module(parent, module_name)
            if retval is not None:
                yield (module_name, retval)
