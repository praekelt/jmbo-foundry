from foundry.settings import *

LAYERS = {
    'layers': ('basic', 'web'),
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
