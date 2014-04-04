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

# Disable celery
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

# Need this last line until django-setuptest is improved.
