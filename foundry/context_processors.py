from django.contrib.sites.models import get_current_site
from django.conf import settings

from foundry.utils import get_preference


def foundry(request):
    # get_preferencem get_current_site do caching
    return {
        'FOUNDRY': settings.FOUNDRY,
        'LAYER_PATH': settings.FOUNDRY['layers'][0] + '/',
        'CURRENT_SITE': get_current_site(request),
        'ANALYTICS_TAGS': get_preference('GeneralPreferences', 'analytics_tags'),
        'SITE_DESCRIPTION': get_preference('GeneralPreferences', 'site_description'),
        'FOUNDRY_HAS_FACEBOOK_CONNECT': getattr(settings, 'FACEBOOK_APP_ID', '') != '',
        'FOUNDRY_HAS_TWITTER_OAUTH': getattr(settings, 'TWITTER_CONSUMER_KEY', '') != '',
    }
