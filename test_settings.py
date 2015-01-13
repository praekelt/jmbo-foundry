from os.path import expanduser

from foundry.settings import *

# Postgis because we want to test full functionality
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'jmbo_spatial',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# See setup.py for an explanation as to why these aren't enabled by default
'''
INSTALLED_APPS += (
    'banner',          # requires dfp
    #'jmbo_calendar',   # requires atlas
    'chart',
    #'competition',
    'downloads',
    'friends',
    'gallery',
    'music',
    'poll',
    #'show',            # requires jmbo_calendar
    #'jmbo_twitter',
)
'''

CKEDITOR_UPLOAD_PATH = expanduser('~')

# Disable celery
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

# xxx: get tests to pass with migrations
SOUTH_TESTS_MIGRATE = False
