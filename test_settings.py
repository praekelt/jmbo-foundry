from foundry.settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'foundry',
        'USER': 'test',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
