from foundry.settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.backends.spatialite',
        'NAME': 'test_foundry.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
