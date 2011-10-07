DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

ROOT_URLCONF = 'foundry.urls'

INSTALLED_APPS = (
    # This application
    'foundry',
    'south',
    'generate',

    # Jmbo minimum
#    'photologue',
    'jmbo',
    'category',
    'publisher',
#    'preferences',
#    'post',
#    'secretballot',
#    'likes',

    # Django minimum
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
)

TEMPLATE_LOADERS = (
    'foundry.loaders.TypeLoader',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

AUTHENTICATION_BACKENDS = (
    'foundry.backends.MultiBackend',
    'django.contrib.auth.backends.ModelBackend',
)

CKEDITOR_MEDIA_PREFIX = '/media/ckeditor/'
#SITE_ID = 1
#TEMPLATE_TYPE = "basic"
#LOGIN_URL = '/login'
#LOGIN_REDIRECT_URL = '/'

# Will be removed when django-profile gets refactored
AUTH_PROFILE_MODULE = 'foundry.Member'
