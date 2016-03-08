from os.path import expanduser

from foundry.settings import *


DATABASES = {
    'default': {
        #'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #'NAME': 'jmbo_spatial',
        'NAME': 'jmbo',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Foundry provides high-level testing tools for other content types
INSTALLED_APPS += (
    'banner',
    'chart',
    'competition',
    'downloads',
    'friends',
    'gallery',
    'jmbo_calendar',
    'jmbo_sitemap',
    'jmbo_twitter',
    'music',
    'poll',
    'show',
)

CKEDITOR_UPLOAD_PATH = expanduser('~')

# Disable celery
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

# xxx: get tests to pass with migrations
SOUTH_TESTS_MIGRATE = False
