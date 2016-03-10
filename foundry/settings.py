"""
This is a sample settings.py adapted from the one generated by jmbo-paste. It
is intended for use in a development environment. You need to change some
private settings before using it in a production environment.
"""

import os
import sys
from os import path
import warnings


FOUNDRY = {
    'sms_gateway_api_key': '',
    'sms_gateway_password': '',
}

LAYERS = {
    'layers': ('basic',),
}

# Paths
SCRIPT_PATH =  path.abspath(path.dirname(__file__))
BUILDOUT_PATH =  path.split(path.abspath(path.join(path.dirname(sys.argv[0]))))[0]

PROJECT_MODULE = 'foundry'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# For older Postgres (location aware) do from command line
# echo "CREATE USER foundry WITH PASSWORD 'foundry'" | sudo -u postgres psql
# echo "CREATE DATABASE foundry WITH OWNER foundry ENCODING 'UTF8' TEMPLATE template_postgis" | sudo -u postgres psql

# For modern Postgres (location aware) do from command line
# echo "CREATE USER foundry WITH PASSWORD 'foundry'" | sudo -u postgres psql
# echo "CREATE DATABASE foundry WITH OWNER foundry ENCODING 'UTF8'" | sudo -u postgres psql
# echo "CREATE EXTENSION postgis" | sudo -u postgres psql foundry
# echo "CREATE EXTENSION postgis_topology" | sudo -u postgres psql foundry

DATABASES = {
    'default': {
        # Must use postgis when developing foundry and Jmbo core itself else migrations are wrong
        #'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'foundry16', # Or path to database file if using sqlite3.
        'USER': 'foundry', # Not used with sqlite3.
        'PASSWORD': 'foundry', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '%s/media/' % BUILDOUT_PATH



# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_ROOT = '%s/static/' % BUILDOUT_PATH

STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't7lf+w70_4w7u4q(ijo&vx19t=%$_03ymp2afr*s8sm0@_3asm'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'foundry.middleware.AgeGateway',
    'foundry.middleware.CheckProfileCompleteness',
    'django.contrib.messages.middleware.MessageMiddleware',
    'likes.middleware.SecretBallotUserIpUseragentMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'foundry.middleware.VerboseRequestMeta',
    'foundry.middleware.LastSeen',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

# A tuple of callables that are used to populate the context in RequestContext.
# These callables take a request object as their argument and return a
# dictionary of items to be merged into the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    'preferences.context_processors.preferences_cp',
    'foundry.context_processors.foundry',
)

TEMPLATE_LOADERS = (
    'layers.loaders.filesystem.Loader',
    'django.template.loaders.filesystem.Loader',
    'layers.loaders.app_directories.Loader',
    'django.template.loaders.app_directories.Loader',
)

ROOT_URLCONF = 'foundry.urls'

INSTALLED_APPS = (
    # The order is important else template resolution may not work
    'foundry',

    # Optional praekelt-maintained apps. Uncomment for development and
    # install with buildout or pip.
    #'banner',          # requires dfp
    #'chart',
    #'competition',
    #'downloads',
    #'friends',
    #'gallery',
    #'jmbo_calendar',
    #'jmbo_sitemap',
    #'jmbo_twitter',
    #'music',
    #'poll',
    #'show',            # requires jmbo_calendar

    'contact',
    'post',
    'jmbo_analytics',
    'jmbo',
    'category',
    'likes',
    'photologue',
    'secretballot',

    #'atlas',
    'captcha',
    'ckeditor',
    'compressor',
    'dfp',
    'export',
    'generate',
    'googlesearch',
    'object_tools',
    'pagination',
    'publisher',
    'preferences',
    'simple_autocomplete',
    'sites_groups',
    'snippetscream',
    'social_auth',
    'south',
    'tastypie',
    'ultracache',

    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    #'django.contrib.gis',
    'django.contrib.sitemaps',
    'django.contrib.admin',

    'djcelery',
    'layers',
)

# Your ReCaptcha provided public key.
RECAPTCHA_PUBLIC_KEY = '6LccPr4SAAAAAJRDO8gKDYw2QodyRiRLdqBhrs0n'

# Your ReCaptcha provided private key.
RECAPTCHA_PRIVATE_KEY = '6LccPr4SAAAAAH5q006QCoql-RRrRs1TFCpoaOcw'

# URL prefix for ckeditor JS and CSS media (not uploaded media). Make sure to use a trailing slash.
CKEDITOR_MEDIA_PREFIX = '/media/ckeditor/'

# Specify absolute path to your ckeditor media upload directory.
# Make sure you have write permissions for the path, i.e/home/media/media.lawrence.com/uploads/
CKEDITOR_UPLOAD_PATH = '%s/media/uploads/' % BUILDOUT_PATH

CKEDITOR_CONFIGS = {
    'default': {'toolbar_Full': [
        ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
        ['Link', 'Image', 'Flash', 'PageBreak'],
        ['TextColor', 'BGColor'],
        ['Smiley', 'SpecialChar'], ['Source'],
    ]},
}

# LASTFM_API_KEY = '' # custom - fix in paster

LOGIN_URL = '/login'        # check if in paster

LOGIN_REDIRECT_URL = '/'    # check if inpaster

# todo: add setting to foundry paster
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'foundry.backends.MultiBackend',
    'django.contrib.auth.backends.ModelBackend',
)

COMMENTS_APP = 'foundry'

SIMPLE_AUTOCOMPLETE = {
    'auth.user': {'threshold': 20, 'search_field': 'username'},
    'category.category': {'threshold':20},
    'jmbo.modelbase': {
        'threshold': 20,
        'duplicate_format_function': lambda item, model, content_type: item.as_leaf_class().content_type.name
    }
}

STATICFILES_FINDERS = (
    'layers.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'layers.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
)

JMBO_ANALYTICS = {
    'google_analytics_id': '',
}

PHOTOLOGUE_MAXBLOCK = 2 ** 20

DJANGO_ATLAS = {
    'google_maps_api_key': 'AIzaSyBvdwGsAn2h6tNI75M5cAcryln7rrTYqkk',
}


# See django-socialauth project for all settings
SOCIAL_AUTH_USER_MODEL = 'foundry.Member'
#FACEBOOK_APP_ID = ''
#FACEBOOK_API_SECRET = ''
#TWITTER_CONSUMER_KEY = ''
#TWITTER_CONSUMER_SECRET = ''
#GOOGLE_OAUTH2_CLIENT_ID = ''
#GOOGLE_OAUTH2_CLIENT_SECRET = ''

INTERNAL_IPS = ('127.0.0.1',)

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

import djcelery
djcelery.setup_loader()
