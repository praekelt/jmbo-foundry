from foundry.settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'test_foundry.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# We don't need migrations in tests
li = list(INSTALLED_APPS)
li.remove('south')
INSTALLED_APPS = tuple(li)

# Re-enable once south's test management command is reinstated
# SOUTH_TESTS_MIGRATE = False
