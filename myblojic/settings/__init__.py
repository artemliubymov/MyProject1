from .django import *

try:
    from .local import *
except ImportError:
    pass
