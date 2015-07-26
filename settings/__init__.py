from settings.django import *

try:
    from settings.local import *
except ImportError:
    pass
