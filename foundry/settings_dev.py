from foundry.settings import *

#FOUNDRY['layers'] =  ('basic',)
#FOUNDRY['layers'] =  ('smart', 'basic',)
FOUNDRY['layers'] =  ('web', 'basic',)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
