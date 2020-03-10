import sys
import types

from .__meta__ import version as __version__
from .descriptors import metaclass, decorate, class_value, class_property


__all__ = ['__version__', 'metaclass', 'decorate', 'class_value', 'class_property']


class ClassPropertyModule(types.ModuleType):
    """Custom module to allow the module to be called to use the class_property."""
    __version__ = __version__

    class_value = class_value
    class_property = class_property
    metaclass = staticmethod(metaclass)
    decorate = staticmethod(decorate)

    def __call__(self, fget=None, fset=None, fdel=None, doc=''):
        """Class property that shares the same value with the class and any instance."""
        return self.class_property(fget, fset, fdel, doc)


sys.modules[__name__] = ClassPropertyModule(__name__)
