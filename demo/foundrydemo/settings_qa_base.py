from foundrydemo.settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'foundrydemo_qa',
        'USER': 'foundrydemo_qa',
        'PASSWORD': 'foundrydemo_qa',
        'HOST': '',
        'PORT': '',
    }
}

MEDIA_ROOT = '%s/../media-qa/' % BUILDOUT_PATH

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'foundrydemo_qa',
    }
}

CKEDITOR_UPLOAD_PATH = '%s/../media-qa/uploads/' % BUILDOUT_PATH
